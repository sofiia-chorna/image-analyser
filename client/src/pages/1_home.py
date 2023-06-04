import streamlit as st
import json
import torch
import cv2
import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from processor.config import config
from processor.image_processor import ImageRunner

@st.cache_data()
def load_list_of_images_available(
        all_image_files: dict,
        image_files_dtype: str,
        clothes_type: str
) -> list:
    """Retrieves list of available images given the current selections"""
    types_dict = all_image_files.get(image_files_dtype)
    list_of_files = types_dict.get(clothes_type.lower())
    return list_of_files


@st.cache_data()
def load_s3_file_structure(path: str = 'all_image_files.json') -> dict:
    """Retrieves JSON document outing the S3 file structure"""
    with open(path, "r") as f:
        return json.load(f)


if __name__ == '__main__':
    all_image_files = load_s3_file_structure()
    n_classes = len(config['all_classes'])
    model = torch.load(config['model'], map_location=torch.device('cpu'))
    for param in model.parameters():
        param.requires_grad = False
    model.eval()

    types_of_clothes = sorted(list(all_image_files['test'].keys()))
    types_of_clothes = [clothes.title() for clothes in types_of_clothes]

    st.title('Welcome to Clothes Segmentation Project!')
    st.write("""
            Either upload your own image or select from
            the sidebar to get a preconfigured image.
            The image you select or upload will be fed
            through the Deep Neural Network in real-time
            and the output will be displayed to the screen.
            """)
    threshold = st.slider('Threshold value', 0, 100, 75)

    uploaded_file = st.file_uploader("Choose an image...")
    img = None
    if uploaded_file is not None:  # if user uploaded file
        st.image(uploaded_file, caption='Input Image', use_column_width=True)
        img = Image.open(uploaded_file)
        m = np.array(img)
        m = cv2.resize(m, (362, 562), interpolation=cv2.INTER_AREA)

        with st.spinner('Processing the image...'):
            result_file, result_class_ids, result_class_names, result_scores = ImageRunner(model, m, threshold).process_image()

        st.header(f"Here is the result of segmentation:")
        img = Image.open(result_file)
        resized_image = img.resize((336, 562))
        st.image(resized_image, caption='Clothes Segmentation')
        with open(result_file, "rb") as file:
            btn = st.download_button(
                label="Download result image",
                data=file,
                file_name="segmentation_result.png",
                mime="image/png"
            )

        st.subheader("Analyses scores")

        # Convert scores to percentages
        result_scores_percent = [f'{score * 100:.2f}%' for score in result_scores]

        # Create a list of tuples combining the data
        data = list(zip(result_class_names.values(), result_scores_percent))

        # Create a DataFrame from the list of tuples
        df = pd.DataFrame(data, columns=['Class Name', 'Score'])
        st.dataframe(df, use_container_width=True)

        # Create a bar chart using Plotly
        fig = go.Figure(data=go.Bar(x=list(result_class_names.values()), y=result_scores))

        # Customize the chart layout
        fig.update_layout(
            xaxis_title="Class",
            yaxis_title="Score",
        )

        st.subheader("Chart view")

        # Display the chart using Streamlit
        st.plotly_chart(fig)


        # Create a dictionary combining the data
        data = {
            "tags": [
                {
                    "class_name": result_class_names[class_id],
                    "confidence": score
                }
                for class_id, score in zip(result_class_ids, result_scores)
            ]
        }

        st.subheader("JSON view")

        # Display the data as JSON using Streamlit
        st.json(data)

import { Abstract } from '../abstract/abstract.repository.js';

export class Collection extends Abstract {
  /**
   * @return {Collection}
   */
  constructor({ collectionModel }) {
    super(collectionModel);
  }

  /**
   * @private
   * @return {Promise<!Array<!Object>>}
   */
  async getCollections() {
    return await this.getAll();
  }

  /**
   * @private
   * @param {string} id
   * @return {Promise<Object>}
   */
  async getCollectionById(id) {
    return await this.getById(id);
  }

  /**
   * @private
   * @param {Object} collection
   * @return {Object}
   */
  async insertCollection(collection) {
    if (collection) {
      const label = this.getLabel();
      const query = `CREATE (n:${label} { name: $name, description: $description }) RETURN n`;
      const { name, description } = collection;
      return await this.neo4j.write(query, { name: name, description: description });
    }
    return await this.create();
  }

  /**
   * @private
   * @param {string} id
   * @param {Object} collection
   * @return {Object}
   */
  async updateCollection(id, collection) {
    return await this.updateById(id, collection);
  }

  /**
   * @private
   * @param {string} id
   * @return {Promise<Object>}
   */
  async deleteCollection(id) {
    return await this.deleteById(id);
  }
}

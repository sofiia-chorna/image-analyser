import { ApiPath } from '../common/common.js';
import { initCollection } from './collection/collection.api.js';

export function initApi(fastify, options, done) {
  // Retrieve services
  const { services: { collection } } = options;

  // Validate scheme of data
  // fastify.setValidatorCompiler(({ schema }) => {
  //   return data => schema.validate(data);
  // });

  // Register collection path & service
  fastify.register(initCollection, {
    services: {
      collection: collection,
    },
    prefix: ApiPath.COLLECTIONS
  });

  done();
}

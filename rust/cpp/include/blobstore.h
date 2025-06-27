#ifndef BLOBSTORE_H
#define BLOBSTORE_H

// include/blobstore.h
#include <memory>

class BlobstoreClient {
public:
  BlobstoreClient();
};

std::unique_ptr<BlobstoreClient> new_blobstore_client();


#endif /* BLOBSTORE_H */

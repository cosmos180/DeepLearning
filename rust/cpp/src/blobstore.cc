/*
 * @Author       : bughero bughero2012@gmail.com
 * @Date         : 2025-06-06 17:30:10
 * @LastEditors  : bughero bughero2012@gmail.com
 * @LastEditTime : 2025-06-06 18:06:59
 * @FilePath     : /DeepLearning/rust/cpp/src/blobstore.cc
 * @Description  : 
 * 
 * Copyright (c) 2025 by @Me, All Rights Reserved. 
 */
// src/blobstore.cc

#include "../include/blobstore.h"

#include <stdio.h>

BlobstoreClient::BlobstoreClient() {}

std::unique_ptr<BlobstoreClient> new_blobstore_client() {
  printf("Creating a new BlobstoreClient instance.\n");
  return std::unique_ptr<BlobstoreClient>(new BlobstoreClient());
}
#!/bin/sh

echo "Processing tags: '${DOCKER_IMAGE_TAGS}'."
readarray -t DOCKER_IMAGE_TAGS <<< "$DOCKER_IMAGE_TAGS"
main_tag=${DOCKER_IMAGE_TAGS[0]}

echo "Building docker image with main tag: '$main_tag'."
docker build --no-cache --progress=plain -t $main_tag -f Dockerfile .
for image_tag in ${DOCKER_IMAGE_TAGS[@]};
do
    echo "Tagging docker image: '$main_tag' wtih tag: '$image_tag'."
    docker tag $main_tag $image_tag
done

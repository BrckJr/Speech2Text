#!/bin/bash

# Clean up the output directory by removing all existing files
# This includes all raw audio files as well as all transcriptions

rm -rf output/raw_audio/*
rm -rf output/transcription/*


echo "Output directories cleaned up."

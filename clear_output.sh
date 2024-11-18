#!/bin/bash

# Clean up the output directory by removing all existing files
# This includes all raw audio files as well as all transcriptions

echo "Deleting output directories ..."

rm -rf output/raw_audio/*
rm -rf output/transcription/*

echo "All contents from the output directories are cleared."

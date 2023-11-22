#!/bin/bash
## source .secrets.sh


OPENAI_API_KEY="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"


curl https://api.openai.com/v1/embeddings \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer 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" \
 -d '{
   "input": "Your text string goes here",
   "model": "text-embedding-ada-002"
 }'

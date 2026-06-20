# Stage 1: Builder

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv export \
    --frozen \
    --no-dev \
    --no-editable \
    --no-hashes \
    --python 3.13 \
    -o requirements.txt

# Stage 2: Lambda runtime

FROM public.ecr.aws/lambda/python:3.13

COPY --from=builder /app/requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

COPY api ${LAMBDA_TASK_ROOT}/api
COPY db ${LAMBDA_TASK_ROOT}/db
COPY rag ${LAMBDA_TASK_ROOT}/rag
COPY utils.py ${LAMBDA_TASK_ROOT}/utils.py
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/lambda_handler.py

CMD ["lambda_handler.handler"]

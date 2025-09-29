.PHONY: build run test

default: build


build:
	cargo build --release

run:
	cargo run -- --debug

test:
	cargo test -- --nocapture

test_chat:
	OPENAI_API_KEY=sk-a01601ba5ce44aab9cccf781b07818be cargo test test_analyze_image_buffer_sync -- --nocapture
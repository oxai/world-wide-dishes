import argparse
import json
import os
import time

import tqdm

import sglang as sgl
from sglang.test.test_utils import (
    add_common_sglang_args_and_parse,
    select_sglang_backend,
)
from sglang.utils import dump_state_text, read_jsonl


@sgl.function
def image_qa(s, image_file, question):
    s += sgl.user(sgl.image(image_file) + question)
    s += sgl.assistant(sgl.gen("answer", max_tokens=args.max_tokens))


def main(args):
    lines = read_jsonl(args.question_file)[: args.num_questions]
    print(f"Reading the json file:{args.question_file}")
    arguments = [
        {
            "image_file": os.path.abspath(l["image_path"]),
            "question": l["question"],
        }
        for l in lines
    ]

    states = [None] * len(lines)

    # Select backend
    print("Setting up the backend")
    backend = select_sglang_backend(args)
    sgl.set_default_backend(backend)

    # Run requests
    tic = time.time()
    print("Running up the backend")
    if args.parallel == 1:
        for i in tqdm.tqdm(range(len(lines))):
            image_file = arguments[i]["image_file"]
            question = arguments[i]["question"]
            ret = image_qa.run(image_file=image_file, question=question, temperature=0)
            states[i] = ret
    else:
        states = image_qa.run_batch(
            arguments, temperature=0, num_threads=args.parallel, progress_bar=True
        )
    latency = time.time() - tic

    print(f"Latency: {latency:.3f}")

    # Write results
    # dump_state_text(f"tmp_output_{args.backend}.txt", states)

    print(f"Write output to {args.answer_file}")
    with open(args.answer_file, "w") as fout:
        for i in range(len(lines)):
            value = {
                "question_id": lines[i]["question_id"],
                "prompt": lines[i]["question"],
                "text": states[i]["answer"].strip(),
                "model_id": backend.model_info["model_path"],
                "answer_id": i,
                "metadata": {},
            }
            fout.write(json.dumps(value) + "\n")

    with open(args.result_file, "a") as fout:
        value = {
            "task": "llava_bench",
            "backend": args.backend,
            "num_gpus": 1,
            "latency": round(latency, 3),
            "num_requests": len(lines),
            "parallel": args.parallel,
        }
        fout.write(json.dumps(value) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question-file", type=str, default="vga_questions.jsonl")
    parser.add_argument("--answer-file", type=str, default="vga_answers.jsonl")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--num-questions", type=int, default=None)
    parser.add_argument("--max-tokens", type=int, default=768)
    args = add_common_sglang_args_and_parse(parser)
    main(args)

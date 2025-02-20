#!/usr/bin/env python

import argparse
import jsonlines
import pandas as pd


system_prompt = "Your role as an assistant involves thoroughly exploring questions through a systematic long thinking process before providing the final precise and accurate solutions. This requires engaging in a comprehensive cycle of analysis, summarizing, exploration, reassessment, reflection, backtracing, and iteration to develop well-considered thinking process. Please structure your response into two main sections: Thought and Solution. In the Thought section, detail your reasoning process using the specified format: <|begin_of_thought|> {thought with steps separated with '\n\n'} <|end_of_thought|> Each step should include detailed considerations such as analisying questions, summarizing relevant findings, brainstorming new ideas, verifying the accuracy of the current steps, refining any errors, and revisiting previous steps. In the Solution section, based on various attempts, explorations, and reflections from the Thought section, systematically present the final solution that you deem correct. The solution should remain a logical, accurate, concise expression style and detail necessary step needed to reach the conclusion, formatted as follows: <|begin_of_solution|> {final formatted, precise, and clear solution} <|end_of_solution|> Now, try to solve the following question through the above guidelines:"


def convert_data(df, version=2, verbose=True):
    """
    Converts data (dictionary) to an instruction tuning format
      - Format ver 1: (with system_prompt)
        {
            "system_prompt": "",
            "question": "",
            "response": ""
        }
      - Format ver 2: (without system_prompt)
        {
            "instruction": "",
            "context": "",
            "response": ""
        }
    """

    new_data = []
    for row_idx, row in df.iterrows():
        question = row['question']
        solution = row['solution']
        answer = row['answer']

        if version == 1:
            new_data.append({
                "system_prompt": system_prompt,
                "question": question,
                "response": solution
            })
        else:
            new_data.append({
                "instruction": question,
                "context": "",
                "response": solution
            })

        if verbose:
            print(f'-----Question {row_idx}-----')
            print(f'**Question**: {question}')
            # print(f'**Solution**: {solution}')
            print(f'**Answer**: {answer}')

    return new_data


def main(args):
    if args.jsonl == '':
        output_jsonl = args.hf_path.split('/')[-1]
    else:
        output_jsonl = args.jsonl

    df = pd.read_json(args.hf_path, lines=True)
    data = convert_data(df)
    with jsonlines.open(output_jsonl, mode='w') as writer:
        writer.write_all(data)
    print(f'Saved HF dataset {args.hf_path} to `{output_jsonl}`')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--hf_path', type=str, required=True)
    parser.add_argument('--jsonl', type=str, default='')
    args = parser.parse_args()
    main(args)

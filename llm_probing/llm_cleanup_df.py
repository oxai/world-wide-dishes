import argparse
import logging
import os
import json
import traceback

import colorlog
import pandas as pd

import sys

sys.path.append(".")

from llm_probing.call_llm import call_chatbot


def setup_logging():
    root = logging.getLogger()
    format      = '%(asctime)s - %(levelname)-s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if 'colorlog' in sys.modules and os.isatty(2):
        cformat = '%(log_color)s' + format
        f = colorlog.ColoredFormatter(cformat, date_format,
              log_colors = { 'DEBUG'   : 'reset',       'INFO' : 'reset',
                             'WARNING' : 'bold_yellow', 'ERROR': 'bold_red',
                             'CRITICAL': 'bold_red' })
    else:
        f = logging.Formatter(format, date_format)
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    root.addHandler(ch)

setup_logging()
log = logging.getLogger(__name__)

autoclean_triggered = False


class AutocleanFailedError(Exception):
    ...


def _autoclean(data, schema, n_retries=3):
    try:
        if schema == "str":
            assert isinstance(data, str)
            return data
        elif schema == "bool":
            results = eval(data)
            assert isinstance(eval(data), bool)
            return results
        elif schema == "int":
            results = eval(data)
            assert isinstance(eval(data), int)
            return results
        elif schema == "float":
            results = eval(data)
            assert isinstance(eval(data), float)
            return results
        elif isinstance(schema, list):
            results = eval(data)
            assert isinstance(eval(data), list)
            if len(schema) != 1:
                raise Exception("Only one type of list is supported")
            return [_autoclean(str(x), schema[0]) for x in results]
        elif isinstance(schema, dict):
            results = eval(data)
            assert isinstance(eval(data), dict)
            return {k: _autoclean(str(v), schema[k]) for k, v in results.items()}
        else:
            raise NotImplementedError
    except (AssertionError, SyntaxError, NameError, TypeError) as e:
        error_message = traceback.format_exc().split("in _autoclean\n")[-1]
        error_prompt = f"data = {data} does not match schema: {schema}\nError while executing: {error_message}\nCorrect the content of ```data = {data}```. Try to adhere to the original data as much as possible. Return it as ```python\n\ndata = <your answer here>\n```"
        if n_retries > 0:
            global autoclean_triggered
            autoclean_triggered = True
            response = call_chatbot([error_prompt], model="gpt35", n=1)[0].strip()
            response = response.split("data = ")[-1]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            return _autoclean(response, schema, n_retries=n_retries - 1)
        raise AutocleanFailedError(f"Failed to autoclean data: {data} with schema: {schema}")


def autoclean(data, schema, n_retries=3, verbose=False):
    global autoclean_triggered
    autoclean_triggered = False
    try:
        results = _autoclean(data, schema, n_retries=n_retries)
        if verbose and autoclean_triggered:
            print(f"Before: {data}")
            print(f"After: {results}")
        return results
    except AutocleanFailedError as e:
        log.warning(str(e))
        return data


def autoclean_df(df, schema, verbose=False):
    for column in df.columns:
        if column in schema:
            df[column] = df[column].apply(lambda row: autoclean(row, schema[column], verbose=verbose))
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--schema", type=str, default="./llm_probing/prompts/autoclean_schema.json")
    args = parser.parse_args()

    df = pd.read_csv(args.path)
    with open(args.schema, "r") as f:
        schema = json.load(f)

    df = autoclean_df(df, schema, verbose=args.verbose)
    # save the cleaned up dataframe
    df.to_csv(args.path.replace(".csv", "_cleaned.csv"), index=False)
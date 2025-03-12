import json
from langchain_core.output_parsers import JsonOutputParser


class CustomJsonOutputParser(JsonOutputParser):
    def get_schema_json(self):
        schema = dict(self._get_schema(self.pydantic_object).items())
        reduced_schema = schema
        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema, ensure_ascii=False)
        return f"""
        OUTPUT JSON SCHEMA:
        {schema_str}
        """
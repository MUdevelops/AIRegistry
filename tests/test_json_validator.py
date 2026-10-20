import unittest

from _helpers import load_component

jv = load_component("json-validator", "json_validator")
old = load_component("json-validator", "json_validator", "1.0.0")

SCHEMA = {
    "type": "object", "required": ["name", "age"], "additionalProperties": False,
    "properties": {"name": {"type": "string", "minLength": 1, "maxLength": 5},
                   "age": {"type": "integer", "minimum": 0, "maximum": 150},
                   "tags": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2},
                   "kind": {"enum": ["a", "b"]}},
}


class TestParsing(unittest.TestCase):
    def test_valid(self):
        r = jv.validate_json('{"b": 1, "a": 2}')
        self.assertTrue(r["valid"])
        self.assertEqual((r["type"], r["keys"]), ("object", ["a", "b"]))

    def test_error_position(self):
        r = jv.validate_json('{\n  "a": ,\n}')
        self.assertFalse(r["valid"])
        self.assertEqual((r["line"], r["column"]), (2, 8))

    def test_types(self):
        for text, kind in (("[1]", "array"), ('"x"', "string"), ("1.5", "number"), ("true", "boolean"), ("null", "null")):
            self.assertEqual(jv.validate_json(text)["type"], kind)

    def test_non_finite_numbers_rejected(self):
        for text in ("NaN", "[Infinity]", "-Infinity"):
            r = jv.validate_json(text)
            self.assertFalse(r["valid"])
            self.assertIn("not valid JSON", r["error"])

    def test_inputs_that_are_not_text(self):
        self.assertIn("str or bytes", jv.validate_json(None)["error"])
        self.assertTrue(jv.validate_json(b'{"a": 1}')["valid"])
        self.assertFalse(jv.validate_json(b"\xff\xfe")["valid"])

    def test_deep_nesting_does_not_crash(self):
        self.assertFalse(jv.validate_json("[" * 100000)["valid"])


class TestSchema(unittest.TestCase):
    def errors(self, text, schema=SCHEMA):
        return jv.validate_json(text, schema)["schema_errors"]

    def test_valid_document(self):
        self.assertEqual(self.errors('{"name": "Ada", "age": 36, "tags": ["x"], "kind": "a"}'), [])

    def test_collects_every_violation_with_paths(self):
        errs = self.errors('{"name": "", "age": -1, "tags": [1, "a", "b"], "kind": "z", "x": 1}')
        joined = "\n".join(errs)
        for fragment in ("$.name: expected at least 1", "$.age: -1 is below", "$.tags[0]: expected string, got number",
                         "$.tags: expected at most 2", "$.kind: value is not one of", "unexpected key 'x'"):
            self.assertIn(fragment, joined)

    def test_required_and_type_mismatch(self):
        self.assertIn("missing required key 'age'", "\n".join(self.errors('{"name": "x"}')))
        self.assertEqual(self.errors("[]"), ["$: expected object, got array"])

    def test_upper_bounds(self):
        self.assertTrue(any("above the maximum" in e for e in self.errors('{"name": "abcdef", "age": 200}')))
        self.assertTrue(any("at most 5 characters" in e for e in self.errors('{"name": "abcdef", "age": 1}')))

    def test_type_lists_and_integer_semantics(self):
        s = {"type": ["string", "null"]}
        self.assertEqual(self.errors("null", s), [])
        self.assertEqual(len(self.errors("1", s)), 1)
        self.assertEqual(self.errors("2.0", {"type": "integer"}), [])
        self.assertEqual(len(self.errors("2.5", {"type": "integer"})), 1)
        self.assertEqual(len(self.errors("true", {"type": "number"})), 1)
        self.assertEqual(len(self.errors("true", {"type": "integer"})), 1)

    def test_malformed_schemas_raise(self):
        for bad in ({"type": "bogus"}, {"type": []}, {"required": "name"}, {"properties": {"a": {"type": "x"}}},
                    {"additionalProperties": "no"}, {"minItems": "1"}, {"minimum": "0"}, {"enum": 1}, [], {"items": 5}):
            with self.assertRaises(ValueError, msg=bad):
                jv.validate_json("{}", bad)

    def test_unsupported_keywords_are_ignored(self):
        self.assertTrue(jv.validate_json("1", {"type": "number", "format": "int32"})["valid"])

    def test_validity_matches_1_0_0(self):
        schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer"}}}
        for text in ('{"a": 1}', '{"a": "x"}', "{}", "[", '{"a": 1.5}'):
            a, b = old.validate_json(text, schema), jv.validate_json(text, schema)
            self.assertEqual(a["valid"], b["valid"], text)
            self.assertEqual(len(a["schema_errors"]), len(b["schema_errors"]), text)


if __name__ == "__main__":
    unittest.main()

from collections import namedtuple

FoundItem = namedtuple("FoundItem", ['item', 'parent', 'line', 'line_number'])
RunData = namedtuple('RunData', ['amount_workers', 'chunk_size', 'time', "executor"])

TemplateItem = namedtuple('TemplateItem', ['item', 'line_number', 'has_error', 'correction', 'is_case_error'])

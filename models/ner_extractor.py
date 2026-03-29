from transformers import pipeline

class PIIAnonymizer:
    def __init__(self):
        # Local minibase.ai NER model (using dslim/bert-base-NER as proxy)
        self.ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
        
    def anonymize(self, text: str) -> str:
        entities = self.ner_pipeline(text)
        anonymized_text = text
        for ent in entities:
            # Replace recognized entity with [PII]
            anonymized_text = anonymized_text.replace(ent['word'], f"[{ent['entity_group']}]")
        return anonymized_text

if __name__ == "__main__":
    extractor = PIIAnonymizer()
    sample = "My name is John Doe from AcmeCorp and I am looking at Salesforce instead."
    print("Original:", sample)
    print("Anonymized:", extractor.anonymize(sample))

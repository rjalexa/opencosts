import { Card, Select, Group, Text } from '@mantine/core';
import { useState, useEffect } from 'react';
import type { Author, Model } from '../../services/api';

interface Props {
  authors: Author[];
  onComparisonModelChange: (model: Model | null) => void;
}

const ModelComparisonCard = ({ authors, onComparisonModelChange }: Props) => {
  const [selectedAuthor, setSelectedAuthor] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [authorOptions, setAuthorOptions] = useState<{ value: string; label: string }[]>([]);
  const [modelOptions, setModelOptions] = useState<{ value: string; label: string }[]>([]);

  // Populate author options
  useEffect(() => {
    const options = authors.map(author => ({
      value: author.name,
      label: author.name
    }));
    setAuthorOptions(options);
  }, [authors]);

  // Populate model options when author is selected
  useEffect(() => {
    if (selectedAuthor) {
      const author = authors.find(a => a.name === selectedAuthor);
      if (author) {
        const options = author.models.map(model => ({
          value: model.id,
          label: model.name
        }));
        setModelOptions(options);
      }
    } else {
      setModelOptions([]);
    }
  }, [selectedAuthor, authors]);

  // Handle author selection
  const handleAuthorChange = (value: string | null) => {
    setSelectedAuthor(value);
    setSelectedModel(null);
    onComparisonModelChange(null);
  };

  // Handle model selection
  const handleModelChange = (value: string | null) => {
    setSelectedModel(value);
    if (value) {
      const author = authors.find(a => a.name === selectedAuthor);
      if (author) {
        const model = author.models.find(m => m.id === value);
        if (model) {
          onComparisonModelChange(model);
        }
      }
    } else {
      onComparisonModelChange(null);
    }
  };

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Group justify="space-between" align="flex-start">
        <Text size="lg" fw={500}>Compare Models</Text>
      </Group>
      <Group mt="md">
        <Select
          label="Family"
          placeholder="Select a family"
          data={authorOptions}
          value={selectedAuthor}
          onChange={handleAuthorChange}
          clearable
          style={{ flex: 1 }}
        />
        <Select
          label="Model"
          placeholder="Select a model"
          data={modelOptions}
          value={selectedModel}
          onChange={handleModelChange}
          disabled={!selectedAuthor}
          clearable
          style={{ flex: 1 }}
        />
      </Group>
    </Card>
  );
};

export default ModelComparisonCard;
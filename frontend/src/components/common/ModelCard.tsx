import { Card, Title, Anchor, Stack, Group, Text } from '@mantine/core';
import type { Model } from '../../services/api';
import ProviderTable from './ProviderTable';

interface Props {
  model: Model;
}

const ModelCard = ({ model }: Props) => {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <Title order={3} style={{ flex: 1 }}>{model.name}</Title>
          {model.creation_date && (
            <Text size="sm" c="dimmed" style={{ whiteSpace: 'nowrap' }}>
              Created {model.creation_date}
            </Text>
          )}
        </Group>
        <Anchor href={model.url} target="_blank" rel="noopener noreferrer">
          {model.url}
        </Anchor>
        <ProviderTable providers={model.providers} />
      </Stack>
    </Card>
  );
};

export default ModelCard;

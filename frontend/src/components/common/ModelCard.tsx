import { Card, Title, Anchor, Stack } from '@mantine/core';
import type { Model } from '../../services/api';
import ProviderTable from './ProviderTable';

interface Props {
  model: Model;
}

const ModelCard = ({ model }: Props) => {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Stack gap="md">
        <Title order={3}>{model.name}</Title>
        <Anchor href={model.url} target="_blank" rel="noopener noreferrer">
          {model.url}
        </Anchor>
        <ProviderTable providers={model.providers} />
      </Stack>
    </Card>
  );
};

export default ModelCard;

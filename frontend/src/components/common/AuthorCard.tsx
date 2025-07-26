import { Accordion, Stack, Badge, Group, Text } from '@mantine/core';
import type { Author } from '../../services/api';
import ModelCard from './ModelCard';

interface Props {
  author: Author;
}

const AuthorCard = ({ author }: Props) => {
  return (
    <Accordion>
      <Accordion.Item value={author.name}>
        <Accordion.Control>
          <Group justify="space-between" wrap="nowrap">
            <Text fw={500} size="lg">
              {author.name}
            </Text>
            <Badge variant="light" size="sm">
              {author.models.length} model{author.models.length !== 1 ? 's' : ''}
            </Badge>
          </Group>
        </Accordion.Control>
        <Accordion.Panel>
          <Stack gap="md">
            {author.models.map(model => (
              <ModelCard key={model.id} model={model} />
            ))}
          </Stack>
        </Accordion.Panel>
      </Accordion.Item>
    </Accordion>
  );
};

export default AuthorCard;

import { Accordion, Stack } from '@mantine/core';
import type { Author } from '../../services/api';
import ModelCard from './ModelCard';

interface Props {
  author: Author;
}

const AuthorCard = ({ author }: Props) => {
  return (
    <Accordion defaultValue={author.name}>
      <Accordion.Item value={author.name}>
        <Accordion.Control>
          {author.name}
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

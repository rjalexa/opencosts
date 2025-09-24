import { useEffect, useState } from 'react';
import { Container, Title, Loader, Center, Stack } from '@mantine/core';
import { fetchData } from './services/api';
import type { Author, Model } from './services/api';
import AuthorCard from './components/common/AuthorCard';
import ModelComparisonCard from './components/common/ModelComparisonCard';

function App() {
  const [data, setData] = useState<Author[]>([]);
  const [loading, setLoading] = useState(true);
  const [comparisonModel, setComparisonModel] = useState<Model | null>(null);

  useEffect(() => {
    const getData = async () => {
      const result = await fetchData();
      // Sort authors alphabetically by name
      const sortedResult = result.sort((a, b) => a.name.localeCompare(b.name));
      setData(sortedResult);
      setLoading(false);
    };
    getData();
  }, []);

  return (
    <Container size="xl" py="md">
      <Title order={1} mb="lg" ta="center">
        OpenRouter Models
      </Title>
      
      {loading ? (
        <Center>
          <Loader size="lg" />
        </Center>
      ) : (
        <Stack gap="md">
          {data.map(author => (
            <AuthorCard key={author.name} author={author} comparisonModel={comparisonModel} />
          ))}
          <ModelComparisonCard
            authors={data}
            onComparisonModelChange={setComparisonModel}
          />
        </Stack>
      )}
    </Container>
  );
}

export default App;

export interface Provider {
  'Model name': string;
  'Model URL': string;
  'OpenRouter model ID': string;
  'Provider': string;
  'Context length': string;
  'Price/input token': string;
  'Price/output token': string;
  'Latency': string;
  'Throughput': string;
  'Creation date': string;
}

export interface Model {
  name: string;
  url: string;
  id: string;
  creation_date?: string;
  providers: Provider[];
}

export interface Author {
  name: string;
  models: Model[];
}

const formatPrice = (price: string): string => {
  if (!price || price === '0') return '$0.00';
  const priceFloat = parseFloat(price);
  if (isNaN(priceFloat)) return price;
  return `$${(priceFloat * 1000000).toFixed(2)}`;
};

// Proper CSV parsing function that handles quoted fields
const parseCSVRow = (row: string): string[] => {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;
  
  for (let i = 0; i < row.length; i++) {
    const char = row[i];
    
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  
  result.push(current.trim());
  return result;
};

export const fetchData = async (): Promise<Author[]> => {
  try {
    // First try to get data from the backend API
    const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:44400';
    const response = await fetch(`${backendUrl}/models`);
    if (response.ok) {
      const data = await response.json();
      
      // Helper function to parse date for sorting
      const parseCreationDate = (dateStr: string): Date => {
        if (!dateStr) return new Date(0); // Very old date for missing dates
        try {
          return new Date(dateStr);
        } catch {
          return new Date(0);
        }
      };
      
      // Format the prices in the response and sort models by creation date
      return data.map((author: Author) => ({
        ...author,
        models: author.models
          .map(model => ({
            ...model,
            providers: model.providers.map(provider => ({
              ...provider,
              'Price/input token': formatPrice(provider['Price/input token']),
              'Price/output token': formatPrice(provider['Price/output token'])
            }))
          }))
          .sort((a, b) => {
            // Sort by creation date, newest first
            const dateA = parseCreationDate(a.creation_date || '');
            const dateB = parseCreationDate(b.creation_date || '');
            return dateB.getTime() - dateA.getTime();
          })
      }));
    }
  } catch (error) {
    console.warn('Backend API not available, falling back to CSV:', error);
  }

  // Fallback to CSV if backend is not available
  const response = await fetch('/openrouter_models_providers.csv');
  const text = await response.text();
  const rows = text.split('\n').slice(1).filter(row => row.trim()); // Filter out empty rows
  const providers: Provider[] = rows.map(row => {
    const fields = parseCSVRow(row);
    const [
      modelName,
      modelUrl,
      modelId,
      provider,
      contextLength,
      priceInput,
      priceOutput,
      latency,
      throughput,
      creationDate
    ] = fields;
    
    return {
      'Model name': modelName || '',
      'Model URL': modelUrl || '',
      'OpenRouter model ID': modelId || '',
      'Provider': provider || '',
      'Context length': contextLength || '',
      'Price/input token': formatPrice(priceInput || '0'),
      'Price/output token': formatPrice(priceOutput || '0'),
      'Latency': latency || '',
      'Throughput': throughput || '',
      'Creation date': creationDate || ''
    };
  });

  const authors: { [key: string]: { [key: string]: Provider[] } } = {};

  providers.forEach(provider => {
    if (!provider['Model name']) return;
    const authorName = provider['Model name'].split(':')[0];
    const modelName = provider['Model name'];

    if (!authors[authorName]) {
      authors[authorName] = {};
    }
    if (!authors[authorName][modelName]) {
      authors[authorName][modelName] = [];
    }
    authors[authorName][modelName].push(provider);
  });

  // Helper function to parse date for sorting
  const parseCreationDate = (dateStr: string): Date => {
    if (!dateStr) return new Date(0); // Very old date for missing dates
    try {
      return new Date(dateStr);
    } catch {
      return new Date(0);
    }
  };

  return Object.entries(authors).map(([authorName, models]) => ({
    name: authorName,
    models: Object.entries(models)
      .map(([modelName, providers]) => ({
        name: modelName,
        url: providers[0]['Model URL'],
        id: providers[0]['OpenRouter model ID'],
        creation_date: providers[0]['Creation date'],
        providers,
      }))
      .sort((a, b) => {
        // Sort by creation date, newest first
        const dateA = parseCreationDate(a.creation_date || '');
        const dateB = parseCreationDate(b.creation_date || '');
        return dateB.getTime() - dateA.getTime();
      }),
  }));
};

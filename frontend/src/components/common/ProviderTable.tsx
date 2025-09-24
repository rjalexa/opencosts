import { Table, ScrollArea } from '@mantine/core';
import type { Provider, Model } from '../../services/api';
import { calculateAveragePrices, calculatePriceRatios } from '../../services/priceUtils';

interface ComparisonData {
  modelName: string;
  averageInputPrice: number;
  averageOutputPrice: number;
  inputRatio: number;
  outputRatio: number;
}

interface Props {
  providers: Provider[];
  comparisonModel?: Model | null;
}

const ProviderTable = ({ providers, comparisonModel }: Props) => {
  // Calculate average prices for the current model
  const currentModelPrices = calculateAveragePrices(providers);
  
  // Calculate comparison data if a comparison model is selected
  let comparisonData: ComparisonData | null = null;
  if (comparisonModel) {
    const comparisonModelPrices = calculateAveragePrices(comparisonModel.providers);
    const ratios = calculatePriceRatios(currentModelPrices, comparisonModelPrices);
    
    comparisonData = {
      modelName: comparisonModel.name,
      averageInputPrice: comparisonModelPrices.averageInputPrice,
      averageOutputPrice: comparisonModelPrices.averageOutputPrice,
      inputRatio: ratios.inputRatio,
      outputRatio: ratios.outputRatio
    };
  }

  // Format price for display
  const formatPrice = (price: number): string => {
    if (price === 0) return '$0.00';
    return `$${(price * 1000000).toFixed(2)}`;
  };

  // Format ratio for display
  const formatRatio = (ratio: number): string => {
    if (ratio === 0) return 'N/A';
    return `${ratio.toFixed(2)}x`;
  };

  return (
    <ScrollArea>
      <Table striped highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Provider</Table.Th>
            <Table.Th>Context Length</Table.Th>
            <Table.Th>Input Price (per 1M tokens)</Table.Th>
            <Table.Th>Output Price (per 1M tokens)</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {providers.map((provider, index) => (
            <Table.Tr key={index}>
              <Table.Td>{provider.Provider}</Table.Td>
              <Table.Td>{provider['Context length']}</Table.Td>
              <Table.Td>{provider['Price/input token']}</Table.Td>
              <Table.Td>{provider['Price/output token']}</Table.Td>
            </Table.Tr>
          ))}
          {comparisonData && (
            <Table.Tr>
              <Table.Td colSpan={1}>Compared to {comparisonData.modelName}</Table.Td>
              <Table.Td></Table.Td>
              <Table.Td>
                {formatPrice(comparisonData.averageInputPrice)} ({formatRatio(comparisonData.inputRatio)})
              </Table.Td>
              <Table.Td>
                {formatPrice(comparisonData.averageOutputPrice)} ({formatRatio(comparisonData.outputRatio)})
              </Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>
    </ScrollArea>
  );
};

export default ProviderTable;

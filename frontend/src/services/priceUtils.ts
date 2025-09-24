import type { Provider } from './api';

export interface AveragePrices {
  averageInputPrice: number;
  averageOutputPrice: number;
}

/**
 * Calculate average input and output prices for a model's providers
 * @param providers Array of providers for a model
 * @returns Object with average input and output prices
 */
export const calculateAveragePrices = (providers: Provider[]): AveragePrices => {
  // Helper function to parse price strings that may be formatted with $ signs
  const parsePrice = (priceStr: string): number => {
    if (!priceStr) return 0;
    // Remove $ signs and any other formatting, then parse
    const cleanedPrice = priceStr.replace(/[$,]/g, '');
    return parseFloat(cleanedPrice);
  };
  
  // Filter out providers with missing or invalid price data
  const validProviders = providers.filter(provider => {
    const inputPrice = provider['Price/input token'];
    const outputPrice = provider['Price/output token'];
    
    const parsedInputPrice = parsePrice(inputPrice);
    const parsedOutputPrice = parsePrice(outputPrice);
    
    // Check if prices are valid numbers
    return (
      inputPrice &&
      outputPrice &&
      !isNaN(parsedInputPrice) &&
      !isNaN(parsedOutputPrice) &&
      parsedInputPrice > 0 &&
      parsedOutputPrice > 0
    );
  });

  if (validProviders.length === 0) {
    return {
      averageInputPrice: 0,
      averageOutputPrice: 0
    };
  }

  // Calculate sum of input and output prices
  const totalInputPrice = validProviders.reduce((sum, provider) => {
    const price = parsePrice(provider['Price/input token']);
    return sum + price;
  }, 0);

  const totalOutputPrice = validProviders.reduce((sum, provider) => {
    const price = parsePrice(provider['Price/output token']);
    return sum + price;
  }, 0);

  // Calculate averages
  const averageInputPrice = totalInputPrice / validProviders.length;
  const averageOutputPrice = totalOutputPrice / validProviders.length;

  return {
    averageInputPrice,
    averageOutputPrice
  };
};

/**
 * Calculate price ratios between two models
 * @param currentModelPrices Average prices for current model
 * @param comparisonModelPrices Average prices for comparison model
 * @returns Object with input and output price ratios
 */
export const calculatePriceRatios = (
  currentModelPrices: AveragePrices,
  comparisonModelPrices: AveragePrices
): { inputRatio: number; outputRatio: number } => {
  // Avoid division by zero
  const inputRatio = comparisonModelPrices.averageInputPrice !== 0 
    ? currentModelPrices.averageInputPrice / comparisonModelPrices.averageInputPrice
    : 0;
    
  const outputRatio = comparisonModelPrices.averageOutputPrice !== 0
    ? currentModelPrices.averageOutputPrice / comparisonModelPrices.averageOutputPrice
    : 0;

  return {
    inputRatio,
    outputRatio
  };
};
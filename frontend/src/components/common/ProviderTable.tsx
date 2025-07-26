import { Table, ScrollArea } from '@mantine/core';
import type { Provider } from '../../services/api';

interface Props {
  providers: Provider[];
}

const ProviderTable = ({ providers }: Props) => {
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
        </Table.Tbody>
      </Table>
    </ScrollArea>
  );
};

export default ProviderTable;

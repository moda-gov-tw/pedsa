import PropTypes from 'prop-types';
import {useEffect, useMemo, useState} from 'react';

// next
import { useSession, } from 'next-auth/react';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';

// third-party
import axios from 'axios';
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import {
  HeaderSort,
} from 'components/third-party/ReactTable';
import { mockSysHealthList } from 'utils/mocek-sys-health-list';
import axiosPlus from 'sections/api/axiosPlus';

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data }) {

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    rows,
  } = useTable(
    {
      columns,
      data,
      initialState: {
          pageIndex: 0, pageSize: 10,
          hiddenColumns: []
      }
    },
    useGlobalFilter,
    useFilters,
    useSortBy,
    useExpanded,
    usePagination,
    useRowSelect
  );

  return (
    <>
      {/*<TableRowSelection selected={Object.keys(selectedRowIds).length} />*/}
      <Stack spacing={3}>
        <Table {...getTableProps()}>
          <TableHead>
            {headerGroups.map((headerGroup, index) => (
              <TableRow {...headerGroup.getHeaderGroupProps()} key={index} sx={{ '& > th:first-of-type': { width: '58px' } }}>
                {headerGroup.headers.map((column, i) => (
                  <TableCell {...column.getHeaderProps([{ className: column.className }])} key={i}>
                    <HeaderSort column={column} sort />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody {...getTableBodyProps()}>
            {rows.map((row, i) => {
              prepareRow(row);
              return (
                <TableRow key={i} {...row.getRowProps()}>
                  {row.cells.map((cell, index) => (
                    <TableCell key={index} {...cell.getCellProps([{ className: cell.column.className }])}>
                      {cell.render('Cell')}
                    </TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Stack>
    </>
  );
}

ReactTable.propTypes = {
  columns: PropTypes.array,
  data: PropTypes.array,
  getHeaderProps: PropTypes.func,
};

const SysHealthTest = () => {
  const theme = useTheme();

  const [healthData, setHealthData] = useState(null);

  async function getHealthData() {
      await axios.post('/api/project/post_containersStatus')
          .then(async(response) => {
              let containers_dict = response.data.container_dict;
              let healthDataTemp = [];
              await Promise.all(
                  await Object.keys(containers_dict).map((c, index) => {
                      healthDataTemp.push({id: index, server_name: c, system_status: containers_dict[c]})
                  })
              )
              setHealthData(healthDataTemp)
          })
          .catch((error) => {
              console.log('error', error);
          })
  }

  useEffect(() => {
      let health_promiseResult = getHealthData();
      // console.log('health_promiseResult', health_promiseResult);
  }, [])

  // console.log('healthData', healthData);

  const columns = useMemo(
    () => [
      {
        Header: '編號',
        accessor: 'id',
        className: 'cell-center',
        disableSortBy: true,
      },
      {
        Header: '服務與伺服器名稱',
        accessor: 'server_name',
        className: 'cell-center',
        disableSortBy: true,
      },
      {
        Header: '狀態',
        accessor: 'system_status',
        className: 'cell-center',
        disableSortBy: true,
      }
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme]
  );



  return (
    <Page title="Customer List">
      {healthData && (
          <MainCard content={false}>
            <ScrollX>
              <ReactTable columns={columns} data={healthData} />
            </ScrollX>
          </MainCard>
      )}
    </Page>
  );
};

SysHealthTest.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default SysHealthTest;

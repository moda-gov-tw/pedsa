import PropTypes from 'prop-types';
import { useEffect, useMemo, useState } from 'react';

// next

// material-ui
import { Stack, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow } from '@mui/material';
import { useTheme } from '@mui/material/styles';

// third-party
import axios from 'axios';
import { useExpanded, useFilters, useGlobalFilter, usePagination, useRowSelect, useSortBy, useTable } from 'react-table';

// project import
import MainCard from 'components/MainCard';
import Page from 'components/Page';
import { HeaderSort } from 'components/third-party/ReactTable';
import Layout from 'layout';

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data }) {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(event.target.value);
    setPage(0);
  };

  function customLabelDisplayedRows({ from, to, count }) {
    return `第${from}–${to}筆 ${count !== -1 ? `共${count}筆` : `超過${to}筆`}`;
  }

  const { getTableProps, getTableBodyProps, headerGroups, prepareRow, rows } = useTable(
    {
      columns,
      data,
      initialState: {
        pageIndex: 0,
        pageSize: 10,
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
        <TableContainer /* sx={{ maxHeight: '100px' }} */>
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
              {rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row, i) => {
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
        </TableContainer>
      </Stack>
      <TablePagination
        sx={{ '.MuiTablePagination-toolbar': { width: '70%' /* , backgroundColor: '#226cea' */ } }}
        labelRowsPerPage="每頁顯示筆數"
        rowsPerPageOptions={[10, 20, 50, 100]}
        labelDisplayedRows={customLabelDisplayedRows}
        component="div"
        count={rows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        showFirstButton
        showLastButton
      />
    </>
  );
}

ReactTable.propTypes = {
  columns: PropTypes.array,
  data: PropTypes.array,
  getHeaderProps: PropTypes.func
};

const SysHealthTest = () => {
  const theme = useTheme();

  const [healthData, setHealthData] = useState(null);

  async function getHealthData() {
    await axios
      .get('/api/sys/get_containersStatus')
      .then(async (response) => {
        let containers_dict = response.data.obj;
        let healthDataTemp = [];
        await Promise.all(
          await containers_dict.map((c, index) => {
            healthDataTemp.push({ id: index, server_name: c.container_name, system_status: c.container_status });
          })
        );
        setHealthData(healthDataTemp);
      })
      .catch((error) => {
        // console.log('error', error);
      });
  }

  useEffect(() => {
    let health_promiseResult = getHealthData();
    // console.log('health_promiseResult', health_promiseResult);
  }, []);

  // console.log('healthData', healthData);

  const columns = useMemo(
    () => [
      {
        Header: '編號',
        accessor: 'id',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '服務與伺服器名稱',
        accessor: 'server_name',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '狀態',
        accessor: 'system_status',
        className: 'cell-center',
        //disableSortBy: true
      }
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme]
  );

  return (
    <Page title="Customer List">
      {healthData && (
        <MainCard content={false} sx={{ marginBottom: '100px' }}>
          {/* <ScrollX> */}
          <ReactTable columns={columns} data={healthData} />
          {/* </ScrollX> */}
        </MainCard>
      )}
    </Page>
  );
};

SysHealthTest.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default SysHealthTest;

import PropTypes from 'prop-types';
import { useEffect, useMemo, useState } from 'react';

// next

// material-ui
import { Stack, Table, TableBody, TableCell, Typography, TableContainer, TableHead, TablePagination, TableRow } from '@mui/material';
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

  const [permissionData, setPermissionData] = useState(null);


  async function getFilePermissionData() {
    await axios
      .get('/api/sys/get_filePermission')
      .then(async (response) => {
        let obj = response.data.obj;
        let filePermissionDataTemp = [];

        let commonPath = obj[0].folder_name;
        obj.forEach((c) => {
          let pathSegments = c.folder_name.split('/');
          let commonSegments = commonPath.split('/');
          let minLength = Math.min(pathSegments.length, commonSegments.length);
          let newCommonPath = [];
  
          for (let i = 0; i < minLength; i++) {
            if (pathSegments[i] === commonSegments[i]) {
              newCommonPath.push(pathSegments[i]);
            } else {
              break;
            }
          }
  
          commonPath = newCommonPath.join('/');
        });

        await Promise.all(
          await obj.map((c, index) => {
            const permissionStatus = c.is_match ? 'Pass' : 'Fail';

            let uniquePath = c.folder_name.replace(commonPath, '');
            if (uniquePath === '') {
              uniquePath = '/';
            }

            filePermissionDataTemp.push({ id: index, folder_name: uniquePath || '/', owner: c.owner, group: c.group, permissions: c.permissions, permission_status: permissionStatus });
          })
        );

        setPermissionData(filePermissionDataTemp);
      })
      .catch((error) => {
        // console.log('error', error);
      });
  }

  useEffect(() => {
    let permission_promiseResult = getFilePermissionData();
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
        Header: '資料夾路徑',
        accessor: 'folder_name',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '擁有者',
        accessor: 'owner',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '所屬群組',
        accessor: 'group',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '讀寫權限資訊',
        accessor: 'permissions',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '比對狀態',
        accessor: 'permission_status',
        className: 'cell-center',
        Cell: ({ value }) => (
          <Typography
            sx={{
              color: value === 'Pass' ? 'green' : 'red',
              fontWeight: 'bold',
            }}
          >
            {value}
          </Typography>
        ),
        //disableSortBy: true
      }
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme]
  );

  return (
    <Page title="Customer List">
      {permissionData && (
        <MainCard content={false} sx={{ marginBottom: '100px' }}>
          {/* <ScrollX> */}
          <ReactTable columns={columns} data={permissionData} />
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

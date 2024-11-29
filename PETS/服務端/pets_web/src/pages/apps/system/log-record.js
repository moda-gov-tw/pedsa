import useClock from 'hooks/useClock';
import PropTypes from 'prop-types';
import { useEffect, useMemo, useState } from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession } from 'next-auth/react';

// material-ui
import {
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  Typography,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers';

// third-party
import { useExpanded, useFilters, useGlobalFilter, usePagination, useRowSelect, useSortBy, useTable } from 'react-table';

// project import
import MainCard from 'components/MainCard';
import Page from 'components/Page';
import ScrollX from 'components/ScrollX';
import { HeaderSort } from 'components/third-party/ReactTable';
import Layout from 'layout';
// import { mockSysLogRecord } from 'utils/mock-log-record.js';
import { GlobalFilter } from '../../../utils/react-table';

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data, setFilter, startDate, setStartDate, endDate, setEndDate }) {
  const theme = useTheme();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
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

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    rows,
    state: { globalFilter },
    preGlobalFilteredRows,
    setGlobalFilter
  } = useTable(
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

  useEffect(() => {
    setFilter(globalFilter);
  }, [globalFilter]);

  useEffect(() => {
    if (startDate) {
      // 預設的endDate是起始日期+2個月(最長查詢區間)
      setEndDate(startDate.add(2, 'month'));
    }
  }, [startDate]);

  return (
    <>
      {/*<TableRowSelection selected={Object.keys(selectedRowIds).length} />*/}
      <Stack spacing={3}>
        <Stack
          direction={matchDownSM ? 'column' : 'row'}
          spacing={1}
          justifyContent="space-between"
          alignItems="center"
          sx={{ p: 3, pb: 0 }}
        >
          <GlobalFilter
            preGlobalFilteredRows={preGlobalFilteredRows}
            globalFilter={globalFilter}
            setGlobalFilter={setGlobalFilter}
            size="small"
          />
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DatePicker
              label="起始日期"
              value={startDate}
              onChange={(d) => {
                setStartDate(d);
              }}
            />
            <DatePicker
              label="結束日期"
              value={endDate}
              onChange={(d) => {
                setEndDate(d);
              }}
              minDate={startDate && startDate.add(1, 'day')}
              maxDate={startDate && startDate.add(2, 'month')}
            />
          </LocalizationProvider>
        </Stack>
        <TableContainer /* sx={{ maxHeight: '100px' }} */>
          <Table {...getTableProps()}>
            <TableHead>
              {headerGroups.map((headerGroup, index) => (
                <TableRow {...headerGroup.getHeaderGroupProps()} key={index} sx={{ '& > th:first-of-type': { width: '300px' } }}>
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

// API: /sys/syslog
const handleFetchSystemLog = async (session, setSysLog, setErrorMsg, startDate, endDate) => {
  const config = {
    headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` }
    // params: {},
  };
  if (startDate && endDate) {
    config.params = { starttime: startDate.format(), endtime: endDate.add(1, 'day').format() };
  }
  const promiseResult = await axiosPlus({
    method: 'GET',
    stateArray: null,
    url: '/api/sys/get_sysLog',
    config: config,
    showSuccessMsg: false
  });

  if (promiseResult.status == 200 && promiseResult.data.status == true) {
    if (promiseResult.data.obj.length > 0) {
      setSysLog(promiseResult.data.obj);
      setErrorMsg((prevObj) => ({ ...prevObj, ['syslog']: null }));
    } else setErrorMsg((prevObj) => ({ ...prevObj, ['syslog']: '無系統紀錄' }));
  } else {
    console.log('ERROR API /sys/syslog:', promiseResult);
    setErrorMsg((prevObj) => ({ ...prevObj, ['syslog']: '錯誤: 無法取得系統紀錄' }));
  }
};

const SysLogRecord = () => {
  const theme = useTheme();
  const { data: session } = useSession();
  const [clockCount] = useClock({ delay: 10 * 1000, restartState: 0, finalState: 60, increaseStep: 1 }); // Automatic counter, increases by 1 every 5 seconds.
  const [sysLog, setSysLog] = useState([]);
  const [errorMsg, setErrorMsg] = useState({});
  const [filter, setFilter] = useState(null);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  const columns = useMemo(
    () => [
      // {
      //   Header: '序號',
      //   accessor: 'id',
      //   className: 'cell-center',
      //   disableSortBy: true,
      // },
      {
        Header: '操作時間',
        accessor: 'sysdatetime',
        className: 'cell-center',
        disableSortBy: true,
        Cell: ({ value }) => {
          if (value) {
            return new Date(value).toLocaleString();
          }
        }
      },
      {
        Header: '操作人',
        accessor: 'useraccount',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: 'Log類別(Info/Error)',
        accessor: 'log_type',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '專案名稱',
        accessor: 'project_name',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: 'Log紀錄',
        accessor: 'logcontent',
        className: 'cell-center',
        //disableSortBy: true
      }
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme]
  );

  useEffect(() => {
    if (!filter) {
      handleFetchSystemLog(session, setSysLog, setErrorMsg, startDate, endDate);
    }
  }, [clockCount]);

  return (
    <Page title="Customer List">
      <MainCard content={false} sx={{ marginBottom: '100px' }}>
        {/* <ScrollX> */}
        <ReactTable
          columns={columns}
          data={sysLog}
          setFilter={setFilter}
          startDate={startDate}
          setStartDate={setStartDate}
          endDate={endDate}
          setEndDate={setEndDate}
        />
        {/* </ScrollX> */}
      </MainCard>
      {errorMsg.syslog ? (
        <>
          <Typography>{errorMsg.syslog}</Typography>
        </>
      ) : (
        <> </>
      )}
    </Page>
  );
};

SysLogRecord.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default SysLogRecord;

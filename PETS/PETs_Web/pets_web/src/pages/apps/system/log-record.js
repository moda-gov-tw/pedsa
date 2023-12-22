import PropTypes from 'prop-types';
import { useEffect, useMemo, useState } from 'react';
import axiosPlus from 'sections/api/axiosPlus';
import useClock from 'hooks/useClock';

// next
import { useSession, } from 'next-auth/react';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
  Box,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  useMediaQuery,
  Typography
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
// import { mockSysLogRecord } from 'utils/mock-log-record.js';
import { GlobalFilter } from "../../../utils/react-table";


// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data }) {
  const theme = useTheme();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    rows,
    state: { globalFilter },
    preGlobalFilteredRows,
    setGlobalFilter,
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
        </Stack>
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

// API: /sys/syslog
const handleFetchSystemLog = async (session, setSysLog, setErrorMsg) => {
  const config = {
    headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
    // params: {},
  };
  const promiseResult = await axiosPlus({
    method: "GET",
    stateArray: null,
    url: "/api/sys/get_sysLog",
    config: config,
    showSuccessMsg: false,
  });

  if (promiseResult.status == 200 && promiseResult.data.status == true) {
    if (promiseResult.data.obj.length > 0) {
      setSysLog(promiseResult.data.obj);
      setErrorMsg(prevObj => ({ ...prevObj, ["syslog"]: null }));
    }
    else
      setErrorMsg(prevObj => ({ ...prevObj, ["syslog"]: "無系統紀錄" }));
  }
  else {
    console.log("ERROR API /sys/syslog:", promiseResult);
    setErrorMsg(prevObj => ({ ...prevObj, ["syslog"]: "錯誤: 無法取得系統紀錄" }));
  }
}

const SysLogRecord = () => {
  const theme = useTheme();
  const { data: session } = useSession();
  const [clockCount] = useClock({ delay: 10 * 1000, restartState: 0, finalState: 60, increaseStep: 1 }); // Automatic counter, increases by 1 every 5 seconds.
  const [sysLog, setSysLog] = useState([]);
  const [errorMsg, setErrorMsg] = useState({});

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
        Cell: ({ value }) => {if(value) {return new Date(value).toLocaleString()}}
      },
      {
        Header: '操作人',
        accessor: 'useraccount',
        className: 'cell-center',
        disableSortBy: true,
      },
      {
        Header: 'Log類別(Info/Error)',
        accessor: 'log_type',
        className: 'cell-center',
        disableSortBy: true,
      },
      {
        Header: '專案名稱',
        accessor: 'project_name',
        className: 'cell-center',
        disableSortBy: true,
      },
      {
        Header: 'Log紀錄',
        accessor: 'logcontent',
        className: 'cell-center',
        disableSortBy: true,
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme]
  );

  useEffect(() => {
    handleFetchSystemLog(session, setSysLog, setErrorMsg);
  }, [clockCount]);

  return (
    <Page title="Customer List">
      <MainCard content={false}>
        <ScrollX>
          <ReactTable columns={columns} data={sysLog} />
        </ScrollX>
      </MainCard>
      {(errorMsg.syslog) ? <>
        <Typography>{errorMsg.syslog}</Typography>
      </> : <> </>}
    </Page>
  );
};

SysLogRecord.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default SysLogRecord;

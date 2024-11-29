import useClock from 'hooks/useClock';
import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { Stack, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers';

// third-party
import axios from 'axios';
import { useExpanded, useFilters, useGlobalFilter, usePagination, useRowSelect, useSortBy, useTable } from 'react-table';

// project import
import MainCard from 'components/MainCard';
import Page from 'components/Page';
import { HeaderSort, TableRowSelection } from 'components/third-party/ReactTable';
import Layout from 'layout';
import { GlobalFilter, renderFilterTypes } from 'utils/react-table';
// import { mockProjectsList } from '../../../utils/mock-projects-list';
import petsLog from 'sections/apps/logger/insert-system-log';

// assets
import { ConfigContext } from '../../../contexts/ConfigContext';
import useUser from '../../../hooks/useUser';

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data, setFilter, startDate, setStartDate, endDate, setEndDate }) {
  // console.log('ReactTable', data);
  const theme = useTheme();
  const router = useRouter();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
  const filterTypes = useMemo(() => renderFilterTypes, []);
  const { userPermission } = useContext(ConfigContext);
  const sortBy = { id: 'fatherName', desc: false };
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

  async function handleAdd() {
    await router.push('/apps/project/new-project');
  }

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    rows,
    state: { globalFilter, selectedRowIds },
    preGlobalFilteredRows,
    setGlobalFilter
  } = useTable(
    {
      columns,
      data,
      filterTypes,
      initialState: {
        pageIndex: 0,
        pageSize: 10,
        sortBy: [sortBy],
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
    // console.log('setFilter');
    setFilter(globalFilter);
  }, [globalFilter]);
  // console.log('globalFilter', globalFilter, selectedRowIds);

  useEffect(() => {
    if (startDate) {
      // console.log('startDate');
      // 預設的endDate是起始日期+2個月(最長查詢區間)
      setEndDate(startDate.add(2, 'month'));
    }
  }, [startDate]);

  return (
    <>
      <TableRowSelection selected={Object.keys(selectedRowIds).length} />
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
                <TableRow {...headerGroup.getHeaderGroupProps()} key={index} sx={{ '& > th:first-of-type': { width: '250px' } }}>
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
  getHeaderProps: PropTypes.func,
  handleAdd: PropTypes.func
};

async function handleFetchProjectLogList(session, setProjectLogList, startDate, endDate) {
  const url = '/api/project/get_jobLog';
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    }
  };
  if (startDate && endDate) {
    config.params = { startDate: startDate.format(), endDate: endDate.add(1, 'day').format() };
  }
  await axios
    .get(url, config)
    .then(async (response) => {
      setProjectLogList(response.data.dataInfo);
    })
    .catch((error) => {
      // console.log('get project job log error', error);
    });
}

const ProjectLogListTable = () => {
  const [clockCount] = useClock({ delay: 10 * 1000, restartState: 0, finalState: 60, increaseStep: 1 }); // Automatic counter, increases by 1 every 5 seconds.
  const theme = useTheme();
  const user = useUser();
  const { data: session } = useSession();
  const [projectLogList, setProjectLogList] = useState([]);
  const [filter, setFilter] = useState(null);
  const [renderedTable, setRenderedTable] = useState(<div>wait</div>);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  // Effect clock & reload
  useEffect(() => {
    if (!filter) {
      // console.log('no filter');
      // Fetch API /projects/list
      handleFetchProjectLogList(session, setProjectLogList, startDate, endDate);
    }
  }, [clockCount]);

  // ReactTable header
  const columns = useMemo(
    () => [
      {
        Header: '專案名稱',
        accessor: 'project_name',
        className: 'cell-center'
      },
      {
        Header: '專案資料夾',
        accessor: 'project_eng',
        className: 'cell-center'
      },
      {
        Header: '專案環境',
        accessor: 'project_env',
        className: 'cell-center'
      },
      {
        Header: '執行job名稱',
        accessor: 'jobname',
        className: 'cell-center'
      },
      // {
      //   Header: '執行步驟',
      //   accessor: 'project_step',
      //   className: 'cell-center'
      // },
      {
        Header: '執行處理程度',
        accessor: 'percentage',
        className: 'cell-center'
      },
      {
        Header: '專案操作內容',
        accessor: 'logcontent',
        className: 'cell-center'
      },
      {
        Header: '專案執行人員',
        accessor: 'useraccount',
        className: 'cell-center'
      },
      {
        Header: '執行開始時間',
        accessor: 'createtime',
        className: 'cell-center'
      },
      {
        Header: '執行開始結束時間',
        accessor: 'updatetime',
        className: 'cell-center'
      },
      {
        Header: '處理時間',
        accessor: 'processtime',
        className: 'cell-center'
      }
    ],
    [theme]
  );

  // Effect: projectList
  useEffect(() => {
    // Render ReactTable
    setRenderedTable(
      <ReactTable
        columns={columns}
        data={projectLogList}
        setFilter={setFilter}
        startDate={startDate}
        setStartDate={setStartDate}
        endDate={endDate}
        setEndDate={setEndDate}
      />
    );
  }, [projectLogList, startDate, endDate]);

  useEffect(() => {
    petsLog(session, 0, `Login User ${user.account} 進入專案操作紀錄列表`);
  }, []);

  return (
    <Page title="Project log List">
      {projectLogList && (
        <MainCard content={false} sx={{ marginBottom: '100px' }}>
          {/* <ScrollX>{renderedTable}</ScrollX> */}
          {renderedTable}
        </MainCard>
      )}
    </Page>
  );
};

ProjectLogListTable.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default ProjectLogListTable;

import useClock from 'hooks/useClock';
import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { Stack, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';

// third-party
import { useExpanded, useFilters, useGlobalFilter, usePagination, useRowSelect, useSortBy, useTable } from 'react-table';

// project import
import MainCard from 'components/MainCard';
import Page from 'components/Page';
import ScrollX from 'components/ScrollX';
import { HeaderSort, TableRowSelection } from 'components/third-party/ReactTable';
import { id_to_join_method_dic } from 'data/join-method';
import Layout from 'layout';
import petsLog from 'sections/apps/logger/insert-system-log';
import { GlobalFilter, renderFilterTypes } from 'utils/react-table';

// assets
import { ConfigContext } from 'contexts/ConfigContext';
import useUser from 'hooks/useUser';
import getALLGroups from 'utils/getGroups';

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data }) {
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
    /* 指定頁碼搜尋框實作參考
    return (
      <>
        <TextField label="" placeholder={`第${from}–${to}筆`} variant="standard" />
        {`第${from}–${to}筆 ${count !== -1 ? `共${count}筆` : `超過${to}筆`}`}
      </>
    ); */
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
        </Stack>
        <TableContainer /* sx={{ maxHeight: '100px' }} */>
          <Table {...getTableProps()} aria-label="custom pagination table">
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

async function handleFetchProjectList(session, [projectList, setProjectList], setAllGroups) {
  await getALLGroups(setAllGroups, session.tocken.loginUserToken);
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    }
  };
  axiosPlus({
    method: 'GET',
    stateArray: [projectList, setProjectList],
    url: '/api/project/get_historyProjectList',
    config: config,
    showSuccessMsg: false
  });
}

const HistoryProjectListTable = () => {
  const [clockCount] = useClock({ delay: 10 * 1000, restartState: 0, finalState: 60, increaseStep: 1 }); // Automatic counter, increases by 1 every 5 seconds.
  const theme = useTheme();
  const user = useUser();
  const { data: session } = useSession();
  const { allGroups, setAllGroups } = useContext(ConfigContext);
  const [historyProjectList, setHistoryProjectList] = useState([]);
  // const [loading, setLoading] = useState(true);
  const [renderedTable, setRenderedTable] = useState(<div>wait</div>);

  // Effect clock & reload
  useEffect(() => {
    // Fetch API /projects/list
    handleFetchProjectList(session, [historyProjectList, setHistoryProjectList], setAllGroups);
  }, []);

  const handleGroupName = (group_id) => {
    let index = allGroups.findIndex(function (temp) {
      return temp.id === group_id;
    });

    return allGroups[index].group_name;
  };

  const handleJoinFuncContent = (join_func) => {
    join_func = JSON.parse(join_func);
    let join_func_indexes = Object.keys(join_func);
    let JoinFuncContentString = '';
    join_func_indexes.map((i) => {
      let jf = join_func[i];
      // if (Number(i)===join_func_indexes.length-1) {
      //   JoinFuncContentString = JoinFuncContentString + `${jf['left_dataset']}_${jf['left_col']}=${jf['right_dataset']}_${jf['right_col']}`
      // }else {
      JoinFuncContentString = JoinFuncContentString + `${jf['left_dataset']}_${jf['left_col']}=${jf['right_dataset']}_${jf['right_col']}\n`;
      // }
    });
    return JoinFuncContentString;
  };

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
        Header: '專案時間',
        accessor: 'createtime',
        className: 'cell-center'
      },
      {
        Header: '專案金鑰',
        accessor: 'enc_key',
        className: 'cell-center'
      },
      {
        Header: '主責單位',
        accessor: 'group_name',
        className: 'cell-center'
        // Cell: ({ value }) => {if(value) {return handleGroupName(value)}}
      },
      {
        Header: '安全鏈結資料集名稱',
        accessor: 'jointablename',
        className: 'cell-center'
      },
      {
        Header: '鏈結後資料筆數',
        accessor: 'jointablecount',
        className: 'cell-center'
      },
      {
        Header: '鏈結方式',
        accessor: 'join_func',
        className: 'cell-center',
        Cell: ({ value }) => {
          if (value || value === 0) {
            return id_to_join_method_dic[Number(value)];
          }
        }
      },
      {
        Header: '鏈結條件',
        accessor: 'join_func_content',
        className: 'cell-center',
        Cell: ({ value }) => {
          if (value) {
            return handleJoinFuncContent(value);
          }
        }
      },
      {
        Header: 'AES加密欄位',
        accessor: 'aes_col',
        className: 'cell-center'
      },
      {
        Header: '專案建立者',
        accessor: 'useraccount',
        className: 'cell-center',
        //disableSortBy: true
      }
    ],
    [theme]
  );

  // Effect: projectList
  useEffect(() => {
    // console.log("projectList", projectList);
    // Render ReactTable
    setRenderedTable(<ReactTable columns={columns} data={historyProjectList} />);

    // Pickout project in connect-processing status
    // pickConnectProcessingProjects(session, projectList, [watchList, setWatchList]);
  }, [historyProjectList]);

  useEffect(() => {
    petsLog(session, 0, `Login User ${user.account} 進入歷史專案列表`);
  }, []);

  return (
    <Page title="Customer List">
      {historyProjectList && (
        <MainCard content={false} sx={{ marginBottom: '100px' }}>
          {/* <ScrollX>{renderedTable}</ScrollX> */}
          {renderedTable}
        </MainCard>
      )}
    </Page>
  );
};

HistoryProjectListTable.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default HistoryProjectListTable;

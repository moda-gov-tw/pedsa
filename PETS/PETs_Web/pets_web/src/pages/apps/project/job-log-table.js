import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import axiosPlus from 'sections/api/axiosPlus';
import useClock from 'hooks/useClock';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { useTheme } from '@mui/material/styles';
import { Button, Stack, Table, TableBody, TableCell, TableHead, TableRow, useMediaQuery } from '@mui/material';

// third-party
import axios from 'axios';
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import { HeaderSort, IndeterminateCheckbox, TableRowSelection } from 'components/third-party/ReactTable';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
// import { mockProjectsList } from '../../../utils/mock-projects-list';
import petsLog from 'sections/apps/logger/insert-system-log';
import { id_to_join_method_dic } from 'data/join-method';

// assets
import { ConfigContext } from '../../../contexts/ConfigContext';
import { PopupTransition } from '../../../components/@extended/Transitions';
import useUser from '../../../hooks/useUser';
import { LocalizationProvider } from '@mui/x-date-pickers';
import getALLGroups from '../../../utils/getGroups';

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data }) {
  // console.log('ReactTable', data);
  const theme = useTheme();
  const router = useRouter();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
  const filterTypes = useMemo(() => renderFilterTypes, []);
  const { userPermission } = useContext(ConfigContext);
  const sortBy = { id: 'fatherName', desc: false };

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
  handleAdd: PropTypes.func
};

async function handleFetchProjectLogList(session, setProjectLogList) {
  const url = '/api/project/get_jobLog';
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    }
  };
  await axios
    .get(url, config)
    .then(async (response) => {
      setProjectLogList(response.data.dataInfo);
    })
    .catch((error) => {
      console.log('get project job log error', error);
    });
}

const ProjectLogListTable = () => {
  const [clockCount] = useClock({ delay: 600 * 1000, restartState: 0, finalState: 60, increaseStep: 1 }); // Automatic counter, increases by 1 every 5 seconds.
  const theme = useTheme();
  const user = useUser();
  const { data: session } = useSession();
  const [projectLogList, setProjectLogList] = useState([]);
  const [renderedTable, setRenderedTable] = useState(<div>wait</div>);

  // Effect clock & reload
  useEffect(() => {
    // Fetch API /projects/list
    handleFetchProjectLogList(session, setProjectLogList);
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
        Header: '執行處理完程度',
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
    setRenderedTable(<ReactTable columns={columns} data={projectLogList} />);
  }, [projectLogList]);

  useEffect(() => {
    petsLog(session, 0, `Login User ${user.account} 進入專案操作紀錄列表`);
  }, []);

  return (
    <Page title="Project log List">
      {projectLogList && (
        <MainCard content={false} sx={{ marginBottom: '100px' }}>
          <ScrollX>{renderedTable}</ScrollX>
        </MainCard>
      )}
    </Page>
  );
};

ProjectLogListTable.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default ProjectLogListTable;

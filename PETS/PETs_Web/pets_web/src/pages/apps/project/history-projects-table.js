import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import axiosPlus from 'sections/api/axiosPlus';
import useClock from 'hooks/useClock';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
  Button,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  useMediaQuery
} from '@mui/material';

// third-party
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import {
  HeaderSort,
  IndeterminateCheckbox,
  TableRowSelection
} from 'components/third-party/ReactTable';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
// import { mockProjectsList } from '../../../utils/mock-projects-list';
import petsLog from 'sections/apps/logger/insert-system-log';

// assets
import { ConfigContext } from "../../../contexts/ConfigContext";
import { PopupTransition } from "../../../components/@extended/Transitions";
import useUser from "../../../hooks/useUser";
import { LocalizationProvider } from "@mui/x-date-pickers";
import getALLGroups from "../../../utils/getGroups";

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
    setGlobalFilter,
  } = useTable(
    {
      columns,
      data,
      filterTypes,
      initialState: {
        pageIndex: 0, pageSize: 10, sortBy: [sortBy],
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
  handleAdd: PropTypes.func,
};

async function handleFetchProjectList(session, [projectList, setProjectList], setAllGroups) {
  await getALLGroups(setAllGroups, session.tocken.loginUserToken);
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    },
  };
  axiosPlus({
    method: "GET",
    stateArray: [projectList, setProjectList],
    url: "/api/project/get_historyProjectList",
    config: config,
    showSuccessMsg: false,
  });
}

const HistoryProjectListTable = () => {
  const [clockCount] = useClock({ delay: 10 * 1000, restartState: 0, finalState: 60, increaseStep: 1 }); // Automatic counter, increases by 1 every 5 seconds.
  const theme = useTheme();
  const user = useUser();
  const router = useRouter();
  const { data: session } = useSession();
  const { allGroups, setAllGroups } = useContext(ConfigContext);
  const [historyProjectList, setHistoryProjectList] = useState([]);
  // const [loading, setLoading] = useState(true);
  const [renderedTable, setRenderedTable] = useState(<div>wait</div>);

  // Effect clock & reload
  useEffect(() => {
    // Fetch API /projects/list
    handleFetchProjectList(session, [historyProjectList, setHistoryProjectList], setAllGroups);
    console.log('allGroups', allGroups);
  }, [])

  const handleGroupName = (group_id) => {
      let index = allGroups.findIndex(function (temp) {
          return temp.id === group_id;
      });

      return allGroups[index].group_name;
    }

  // ReactTable header
  const columns = useMemo(
    () => [
      {
        Header: '歷史專案名稱',
        accessor: 'project_name',
        className: 'cell-center'
      },
      {
        Header: '主責單位',
        accessor: 'group_id',
        className: 'cell-center',
        Cell: ({ value }) => {if(value) {return handleGroupName(value)}}
      },
      {
        Header: '歷史時間',
        accessor: 'createtime',
        className: 'cell-center',
        disableSortBy: true,
      },
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
  }, [historyProjectList])

  useEffect(() => {
    petsLog(session, 0, `Login User ${user.account} 進入歷史專案列表`);
  }, []);

  return (
    <Page title="Customer List">
      {historyProjectList && (
          <MainCard content={false}>
            <ScrollX>
              {renderedTable}
            </ScrollX>
          </MainCard>
      )}
    </Page>
  );
};

HistoryProjectListTable.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default HistoryProjectListTable;
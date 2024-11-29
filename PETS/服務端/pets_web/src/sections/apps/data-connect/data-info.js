import PropTypes from 'prop-types';
import {useContext, useEffect, useMemo, useState} from 'react';
import * as React from 'react';

// material-ui
import {
  Grid,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography
} from '@mui/material';
import MainCard from "../../../components/MainCard";
import ScrollX from "../../../components/ScrollX";
import {renderFilterTypes} from "../../../utils/react-table";
import {HeaderSort, TableRowSelection} from "../../../components/third-party/ReactTable";

// third-party
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data }) {
  // const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
  const filterTypes = useMemo(() => renderFilterTypes, []);
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
    // state: { globalFilter, selectedRowIds },
    // preGlobalFilteredRows,
    // setGlobalFilter,
  } = useTable(
    {
      columns,
      data,
      filterTypes,
      // initialState: {
      //     pageIndex: 0, pageSize: 10, sortBy: [sortBy],
      //     hiddenColumns: []
      // }
    },
    // useGlobalFilter,
    // useFilters,
    // useSortBy,
    // useExpanded,
    // usePagination,
    // useRowSelect
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

const DataInfo = ({ dataInfo= {'dataset_name': 'd1', 'dataset_row_count': 0,
    'columns': [{'col1': 'AES', 'col2': '不處理'}] } }) => {
    function createColumns() {
      dataInfo.columns.push({'欄位名稱': '直接識別處理方式'});
      let columns = [];

      if(dataInfo.columns.length>0) {
          Object.keys(dataInfo.columns[0]).map((key) => {
              columns.push({Header: key, accessor: key, className: 'cell-center', disableSortBy: true});
          })
      }
      console.log('create columns', columns);
      return columns;
    }

    const columns = useMemo(() => {
        return createColumns();
    }, []);
    console.log('columns', columns);


  return (
    <Stack direction={'column'}>
      <Typography variant='h6'>
          資料集名稱: {dataInfo.dataset_name}
      </Typography>
      <Typography variant='subtitle2'>
          資料筆數: {dataInfo.dataset_row_count}
      </Typography>
      <Grid item>
          <MainCard content={false}>
            <ScrollX>
              <ReactTable columns={columns} data={dataInfo.columns} />
            </ScrollX>
          </MainCard>
      </Grid>
    </Stack>
  );
};

export default DataInfo;

import PropTypes from 'prop-types';
import { useEffect, useState, useContext } from 'react';
import * as React from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
  Grid,
  IconButton,
  TextField,
  MenuItem,
  Select,
} from '@mui/material';
import OpenInFullRoundedIcon from '@mui/icons-material/OpenInFullRounded';
import ClearIcon from '@mui/icons-material/Clear';

import { ConfigContext } from 'contexts/ConfigContext';


// ==============================|| COLUMN SELECT ||============================== //

// function ColumnSelect({ start=false, firstColumn=false, prevSelect='', setPrevSelect=() => {}, groups = []}) {
/**
 * Function: ColumnSelect
 *
 * Child component of ConnectSetting
 *
 * @param {{ first: boolean, data: string, setData: func, column: string, setColumn: func, dataConnections: object, setDataConnections: func, index: number }} argObject
 * * `first`: whether it's the left dataset and column.
 * * `data`: dataset name.
 * * `setData`: function to update dataset name.
 * * `column`: column name.
 * * `setColumn`: function to update column name.
 * * `dataConnections`: all data connections in the project.
 * * `setDataConnections`: function for updating dataConnections.
 * * `index`: indxe of the current data connection.
 *
 * @returns {JSX.Element}
 */
function ColumnSelect({ first = true, data = '', setData = () => { }, column = '', setColumn = () => { }, dataConnections, setDataConnections, index}) {

  const { allGroups, setAllGroups, projectGroup, setProjectGroup, status, setStatus, single, setSingle } = useContext(ConfigContext); 

  const [selectedGroup, setSelectedGroup] = useState( ""); 
  const [datasetName,setDatasetName] = useState("");  
  
  let oridataset = "";
  let origroup = "";

  useEffect(() => {
    setDatasetName(data.substring(data.indexOf("_") + 1));
  }, [data]);

  const handleGroupSelect = (event) => {
    setSelectedGroup(event.target.value)
    if(datasetName === "" && data !== ""){
      oridataset = data.substring(data.indexOf('_') + 1);
      setDatasetName(oridataset)
    }
  }

  const handleDatasetName = (event) => {
    setDatasetName(event.target.value)
    if(selectedGroup === "" && data !== ""){
      origroup = data.split("_")[0]
      setSelectedGroup(origroup)
    }
  }


  const handleData = (event) => {
    
    if( datasetName !== '' && selectedGroup !== '' ){

    const combinedName = `${selectedGroup}_${datasetName}`;
    setData(combinedName);

    let newDataConnection = [...dataConnections];
    // console.log('newDataConnection[index]', newDataConnection[index]);
    
    if (first) {
      newDataConnection[index] = {
        ...newDataConnection[index],
        left_datasetname: combinedName,
      };
    } else {
      newDataConnection[index] = {
        ...newDataConnection[index],
        right_datasetname: combinedName,
      };
    }
    setDataConnections(newDataConnection);
  }
  };

  const handleColumn = (event) => {
    setColumn(event.target.value);
    let newDataConnection = [...dataConnections];
    // console.log('newDataConnection[index]', newDataConnection[index]);
    if (first) {
      newDataConnection[index] = {
        ...newDataConnection[index],
        left_col: event.target.value,
      };
    } else {
      newDataConnection[index] = {
        ...newDataConnection[index],
        right_col: event.target.value,
      };
    }
    setDataConnections(newDataConnection);
  };

  return (
    <>
      <Grid container spacing={2} sx={{ 'flex-direction': 'column' }} >
        <Grid container item spacing={2} sx={{ 'flex-direction': 'row' }}>
          <Grid item xs={6}>
            <Select
              value={selectedGroup === '' ? data : selectedGroup}
              displayEmpty
              name="select group name"
              renderValue={(selected) => {
                // if (selected) {
                //   return selected.split('_')[0];
                // } else {
                //   return null;
                // }
                if(selectedGroup !== ''){
                  if (selected) {
                    const selectedGroupObject = projectGroup.length > 0 
                      ? projectGroup.find(g => g.group_type === selected) 
                      : allGroups.find(g => g.group_type === selected);
                    return selectedGroupObject ? selectedGroupObject.group_name : selected;
                  } else {
                    return <span>上傳資料協作單位</span>;
                  }
                }else{  
                  if (selected) {
                    const dataGroupObject = projectGroup.length > 0 
                    ? projectGroup.find(g => g.group_type === data.split('_')[0]) 
                    : allGroups.find(g => g.group_type === data.split('_')[0]);
                    return dataGroupObject ? dataGroupObject.group_name : data.split('_')[0];
                  } else {
                    return <sapn>上傳資料協作單位</sapn>;
                  }
                }
              }}
              fullWidth
              onChange={handleGroupSelect}
              onBlur={handleData}
              // sx={{ "& .MuiInputBase-input": { backgroundColor: "inputBGColor" } }}
            >
            
               {projectGroup.length > 0 ? (
                  projectGroup.map((g) => (
                    <MenuItem value={`${g.group_type}`}>{g.group_name}</MenuItem>
                  ))
                ) : (
                  allGroups.map((g) => (
                    <MenuItem value={`${g.group_type}`}>{g.group_name}</MenuItem>
                  ))
                )}                          
              
            </Select>
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label='資料集名稱'
              value={datasetName}
              onChange={handleDatasetName}
              onBlur={handleData}
              InputLabelProps={{ sx: { lineHeight: "1em" } }}
            />
          </Grid>
        </Grid>
        <Grid item>
        {!(single === 1) && (
            <TextField
              fullWidth
              label='鏈結欄位名稱(多個以","分隔)'
              value={column}
              onChange={handleColumn}
              InputLabelProps={{ sx: { lineHeight: "1em" } }}
            />
        )}
        </Grid>

      </Grid>

    </>
  );
}

/**
 * Function: ConnectSetting
 *
 * Child component of NewProjectDataConnect
 *
 * @param {{ dataConnections: object, setDataConnections: func, index: number }} argObject
 * * `dataConnections`: all data connections in the project.
 * * `setDataConnections`: function for updating dataConnections.
 * * `index`: indxe of the current data connection.
 *
 * @returns {JSX.Element}
 */
const ConnectSetting = ({ dataConnections, setDataConnections, index }) => {
  const theme = useTheme();
  // console.log('dataConnections in ConnectSetting', dataConnections, index);
  // console.log(dataConnections[index]);
  const { status, setStatus, single, setSingle } = useContext(ConfigContext); 
  const [firstData, setFirstData] = useState(dataConnections[index].left_datasetname);
  const [firstColumn, setFirstColumn] = useState(dataConnections[index].left_col);
  const [secondData, setSecondData] = useState(dataConnections[index].right_datasetname);
  const [secondColumn, setSecondColumn] = useState(dataConnections[index].right_col);

  useEffect(() => {
    if(dataConnections[index]) {
      // console.log('set the data');
      setFirstData(dataConnections[index].left_datasetname);
      setFirstColumn(dataConnections[index].left_col);
      setSecondData(dataConnections[index].right_datasetname);
      setSecondColumn(dataConnections[index].right_col)
    }
  }, [dataConnections])

  // useEffect(() => {
  //   if(index && dataConnections[index]) {
  //     console.log('update dataConnections');
  //     console.log('ori dataConnections', [...dataConnections]);
  //     let newDataConnection = [...dataConnections];
  //     console.log('newDataConnection[index]', newDataConnection[index]);
  //     newDataConnection[index] = {
  //       ...newDataConnection[index],
  //       firstData: firstData,
  //       firstColumn: firstColumn,
  //       secondData: secondData,
  //       secondColumn: secondColumn
  //     }
  //     setDataConnections(newDataConnection);
  //   }
  //   console.log('dataConnections', dataConnections);
  // }, [firstData, firstColumn, secondData, secondColumn]);

  return (
    <Grid container spacing={2} columns={11}>
      <Grid item md={5}>
        <ColumnSelect first={true} data={firstData} setData={setFirstData} column={firstColumn} setColumn={setFirstColumn} dataConnections={dataConnections} setDataConnections={setDataConnections} index={index} />
      </Grid>

        
      <Grid container item md={1} justifyContent="center" alignItems='center'>
      {!(single === 1) && (
        <OpenInFullRoundedIcon sx={{ "transform": "rotate(45deg)", 'position': "relative", 'top': "-1px" }} />
      )}
        </Grid>
      <Grid item md={5}>
      {!(single === 1) && (
        <ColumnSelect first={false} data={secondData} setData={setSecondData} column={secondColumn} setColumn={setSecondColumn} dataConnections={dataConnections} setDataConnections={setDataConnections} index={index} />
      )}
      </Grid>
        
      
    </Grid>
  );
};

export default ConnectSetting;


{/*舊的ColumnSelect 選機關(第二組機關選項不會有第一組已經選好的機關)*/ }
{/*{start ? (*/ }
{/*    <TextField*/ }
{/*        fullWidth*/ }
{/*        defaultValue="機關A"*/ }
{/*        InputProps={{*/ }
{/*          readOnly: true,*/ }
{/*        }}*/ }
{/*    />*/ }
{/*) : (*/ }
{/*    <FormControl fullWidth>*/ }
{/*      <InputLabel id="group-select-label">機關</InputLabel>*/ }
{/*      <Select*/ }
{/*            value={selectedGroup}*/ }
{/*            displayEmpty*/ }
{/*            name="select group"*/ }
{/*            onChange={handleChange}*/ }
{/*            renderValue={(selected) => {*/ }
{/*              return selected;*/ }
{/*            }}*/ }
{/*            // onChange={handleChange}*/ }
{/*          >*/ }
{/*          {groupOptions.map((group) => {*/ }
{/*            return <MenuItem value={group} onClick={handleClose}>{group}</MenuItem>*/ }
{/*          })}*/ }
{/*      </Select>*/ }
{/*    </FormControl>*/ }
{/*)}*/ }

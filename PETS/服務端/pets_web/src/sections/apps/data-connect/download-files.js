import * as React from 'react';
import { useMemo } from 'react';
import { FixedSizeList } from 'react-window';

// material-ui
import {
  Box,
  Button,
  Divider,
  Grid,
  InputLabel,
  Stack,
  TextField,
  Typography,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper,
  Link
} from '@mui/material';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import InboxIcon from '@mui/icons-material/Inbox';

// third-party
import axios from 'axios';
import fileDownload from 'js-file-download';

/**
 * Function DownloadFiles
 *
 * @param {{button_name:string, file_name:string, url:string,
 *          icon:React.element, behavior:string, listItemComponent:React.element}} argArray
 * * `button_name` The name shown in download list.
 * * `file_name` The download file name .
 * * `url` The sownload url of file.
 * * `icon` The icon of file.
 * * `behavior`: `download` or `href` (hypertext reference).
 * * `listItemComponent`: default Paper
 * @returns {JSX.Element}
 */
export default function DownloadFiles({
  height = 200,
  argArray = [{ button_name: '', file_name: '', url: '', icon: AttachFileIcon, behavior: 'download', clickFunc: null, disabled: false }],
  listItemComponent = Paper
}) {
  // The `useMemo()` function will only recalculate the value of the variable when the object changes.
  let file_info_array = useMemo(() => {
    return argArray;
  }, []);
  // console.log('DownloadFiles', file_info_array);

  // Render download buttons for Material UI: Virtualized List
  function renderRow(props) {
    // `index` of Material UI: Virtualized List
    const { index, style } = props;
    const handleClick = (url, filename, behavior, clickFunc) => {
      if (behavior == 'download') {
        axios
          .get(url, {
            responseType: 'blob'
          })
          .then((res) => {
            fileDownload(res.data, filename);
          });
      } else if (behavior == 'href') {
        window.location.href = url;
      } else if (behavior == 'exeClickFunc') {
        clickFunc();
      }
    };

    return (
      <ListItem
        style={style}
        key={index}
        component={listItemComponent}
        elevation={1}
        disablePadding
        sx={{ borderRadius: 0, padding: '0 40px' }}
      >
        <ListItemButton
          disabled={argArray[index].disabled}
          onClick={() =>
            handleClick(
              file_info_array[index].url,
              file_info_array[index].file_name,
              file_info_array[index].behavior,
              file_info_array[index].clickFunc
            )
          }
        >
          {/* Icons */}
          <ListItemIcon>
            {file_info_array[index].icon == null ? (
              <AttachFileIcon sx={{ fontSize: 20, transform: 'rotate(45deg)' }} />
            ) : (
              file_info_array[index].icon
            )}
          </ListItemIcon>
          {/* Button Text */}
          <ListItemText primary={`${file_info_array[index].button_name}`} sx={{ ml: 2 }} />
        </ListItemButton>
      </ListItem>
    );
  }

  // Return rendered elements
  return (
    <>
      {/* Download list */}
      <FixedSizeList height={height} width={'100%'} itemSize={40} itemCount={file_info_array.length} overscanCount={5}>
        {renderRow}
      </FixedSizeList>
    </>
  );
}

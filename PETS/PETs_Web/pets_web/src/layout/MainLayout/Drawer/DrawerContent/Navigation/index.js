import { useContext, useEffect, useState } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import { Box, Typography, useMediaQuery } from '@mui/material';

// project import
import NavGroup from './NavGroup';
import menuItem from 'menu-items';

import { useSelector } from 'store';
import useConfig from 'hooks/useConfig';
import { HORIZONTAL_MAX_ITEM } from 'config';
import {ConfigContext} from "contexts/ConfigContext";
import useUser from "hooks/useUser";

// types
import { LAYOUT_CONST } from 'config';
import axios from "axios";
import {useSession} from "next-auth/react";

// ==============================|| DRAWER CONTENT - NAVIGATION ||============================== //

const Navigation = () => {
  const theme = useTheme();
  const user = useUser();
  const { data: session } = useSession();

  const downLG = useMediaQuery(theme.breakpoints.down('lg'));

  const { menuOrientation } = useConfig();
  const { drawerOpen } = useSelector((state) => state.menu);
  const { setUserPermission } = useContext(ConfigContext);
  const [selectedItems, setSelectedItems] = useState('');
  const [selectedLevel, setSelectedLevel] = useState(0);
  const [newMenuItemsState, setNewMenuItemsState] = useState({items: []});

  // 取得登入使用者權限
  function processPermission(user_info) {
    let user_permissions = [];
    if(user_info.is_super_admin) {
      user_permissions.push('super_admin');
    }
    if(user_info.is_group_admin) {
      user_permissions.push('group_admin');
    }
    if(Object.keys(user_info.is_project_admin).length > 0 && user_info.is_project_admin.status) {
      user_permissions.push('project_admin');
    }
    return user_permissions;
  }

  const getUserPermission = async (token) => {
    console.log('getUserPermission');
    await axios.get(`/api/user/get_info/${user.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
        .then(async (response) => {
            console.log('get user permissions', response.data.obj);
            const permissions = await processPermission(response.data.obj);
            console.log('permissions', permissions);
            await createSideBar(permissions);
            setUserPermission(permissions);
        })
        .catch((error) => {
          console.log('get user permissions error', error);
        });
  };

  const createSideBar = (permission) => {
    let newMenuItems = Object.assign({}, menuItem);
    if(!permission.includes('super_admin')) {
      newMenuItems.items = newMenuItems.items.filter(mi => mi.id !== '4'); //sysMenu

      if(!permission.includes('group_admin')) {
        newMenuItems.items = newMenuItems.items.filter(mi => mi.id !== '2'); //groupMenu
        newMenuItems.items = newMenuItems.items.filter(mi => mi.id !== '3'); //userMenu
        // newMenuItems.items = newMenuItems.items.filter(mi => (mi.id !== '2'|| mi.id !== '3')); //groupMenu, userMenu
      }
    }
    console.log('newMenuItems', newMenuItems);
    setNewMenuItemsState(newMenuItems);
  };

  useEffect(() => {
    getUserPermission(session.tocken.loginUserToken);
  }, []);

  const isHorizontal = menuOrientation === LAYOUT_CONST.HORIZONTAL_LAYOUT && !downLG;

  const lastItem = isHorizontal ? HORIZONTAL_MAX_ITEM : null;
  let lastItemIndex = newMenuItemsState.items.length - 1;//menuItem.items.length - 1;
  let remItems = [];
  let lastItemId;

  if (lastItem && lastItem < newMenuItemsState.items.length) {
    lastItemId = newMenuItemsState.items[lastItem - 1].id;
    lastItemIndex = lastItem - 1;
    remItems = newMenuItemsState.items.slice(lastItem - 1, newMenuItemsState.items.length).map((item) => ({
      title: item.title,
      elements: item.children,
      icon: item.icon
    }));
  }

  const navGroups = newMenuItemsState.items.slice(0, lastItemIndex + 1).map((item) => {
    switch (item.type) {
      case 'group':
        return (
          <NavGroup
            key={item.id}
            setSelectedItems={setSelectedItems}
            setSelectedLevel={setSelectedLevel}
            selectedLevel={selectedLevel}
            selectedItems={selectedItems}
            lastItem={lastItem}
            remItems={remItems}
            lastItemId={lastItemId}
            item={item}
          />
        );
      default:
        return (
          <Typography key={item.id} variant="h6" color="error" align="center">
            Fix - Navigation Group
          </Typography>
        );
    }
  });
  return (
    <Box
      sx={{
        pt: drawerOpen ? (isHorizontal ? 0 : 2) : 0,
        '& > ul:first-of-type': { mt: 0 },
        display: isHorizontal ? { xs: 'block', lg: 'flex' } : 'block'
      }}
    >
      {navGroups}
    </Box>
  );
};

export default Navigation;

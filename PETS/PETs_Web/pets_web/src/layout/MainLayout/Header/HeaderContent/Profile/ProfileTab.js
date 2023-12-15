import PropTypes from 'prop-types';

// next
import { useRouter } from 'next/router';

// material-ui
import { List, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import AccountCircleOutlinedIcon from '@mui/icons-material/AccountCircleOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';

// ==============================|| HEADER PROFILE - PROFILE TAB ||============================== //

const ProfileTab = ({ handleLogout }) => {
  const router = useRouter();

  return (
    <List component="nav" sx={{ p: 0, '& .MuiListItemIcon-root': { minWidth: 32 } }}>
      {/*<ListItemButton selected={selectedIndex === 0} onClick={(event) => handleListItemClick(event, 0)}>*/}
      {/*  <ListItemIcon>*/}
      {/*    <EditOutlined />*/}
      {/*  </ListItemIcon>*/}
      {/*  <ListItemText primary="Edit Profile" />*/}
      {/*</ListItemButton>*/}
      {/*<ListItemButton selected={selectedIndex === 1} onClick={(event) => handleListItemClick(event, 1)}>*/}
      {/*  <ListItemIcon>*/}
      {/*    <UserOutlined />*/}
      {/*  </ListItemIcon>*/}
      {/*  <ListItemText primary="View Profile" />*/}
      {/*</ListItemButton>*/}

      {/*<ListItemButton selected={selectedIndex === 3} onClick={(event) => handleListItemClick(event, 3)}>*/}
      {/*  <ListItemIcon>*/}
      {/*    <ProfileOutlined />*/}
      {/*  </ListItemIcon>*/}
      {/*  <ListItemText primary="Social Profile" />*/}
      {/*</ListItemButton>*/}
      {/*<ListItemButton selected={selectedIndex === 4} onClick={(event) => handleListItemClick(event, 4)}>*/}
      {/*  <ListItemIcon>*/}
      {/*    <WalletOutlined />*/}
      {/*  </ListItemIcon>*/}
      {/*  <ListItemText primary="Billing" />*/}
      {/*</ListItemButton>*/}
      {/*selectedIndex === 2*/}
      <ListItemButton selected={true} onClick={() => {router.push('/apps/user/password-reset')}}>
        <ListItemIcon>
          <AccountCircleOutlinedIcon />
        </ListItemIcon>
        <ListItemText primary="個人設定" />
      </ListItemButton>
      <ListItemButton selected={true} onClick={handleLogout}>
        <ListItemIcon>
          <LogoutOutlinedIcon />
        </ListItemIcon>
        <ListItemText primary="登出" />
      </ListItemButton>
    </List>
  );
};

ProfileTab.propTypes = {
  handleLogout: PropTypes.func
};

export default ProfileTab;

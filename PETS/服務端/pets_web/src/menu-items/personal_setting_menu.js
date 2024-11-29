// third-party
import { FormattedMessage } from 'react-intl';

// ==============================|| MENU ITEMS - USER ||============================== //

const personalSettingMenu = {
  id: '6',
  title: <FormattedMessage id=" " />,
  type: 'group',
  children: [
    {
      id: 'password-reset',
      title: <FormattedMessage id="個人設定" />,
      type: 'not-show',
      url: '/apps/user/password-reset',
      breadcrumbs: true
    }
  ]
};

export default personalSettingMenu;

// next
import { useSession } from 'next-auth/react';

/**
 * Function : useUser(登入的使用者資訊)
 *
 * @returns {object} id: 使用者id account: 使用者帳戶名稱
*/
const useUser = () => {
  const { data: session } = useSession();
  // console.log('session', session);
  if (session) {
    // const user = session?.user;
    const user = session?.tocken;
    
    // const provider = session?.provider;
    // let thumb = user?.image;
    // if (provider === 'cognito') {
    //   const email = user?.email?.split('@');
    //   user.name = email ? email[0] : 'Jone Doe';    }

    // if (!user?.image) {
    //   user.image = '/assets/images/users/avatar-1.png';
    //   thumb = '/assets/images/users/avatar-thumb-1.png';
    // }

    const newUser = {
      id: user.id,
      account: user.account,
    };

    return newUser;
  }
  return false;
};

export default useUser;

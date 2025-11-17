from flask import session
from util.ip_addr import ip_addr
from util.logger import log
from app_config import ldap_admins, admin_deps, permit_post

     
class SSO_User:
    def get_user_by_name(self, src_user):
        ip = ip_addr()
        self.src_user = src_user
        self.post=''
        self.dep_name=''
        self.roles=''
        self.top_control=0

        if 'password' in session:
            self.password = session['password']
        if src_user and 'login_name' in src_user:
            log.debug(f'SSO_USER. src_user: {src_user}')

            login_name = src_user['login_name']
            self.username = login_name
            session['username'] = login_name

            if 'dep_name' in src_user and src_user['dep_name'] in admin_deps:
                self.top_control=1

            if self.top_control==0 and ('post' not in src_user or src_user['post'] not in permit_post):
                log.info(f'----------------\n\tUSER {session['username']} not Registred\n----------------')
                return None

            if 'dep_name' in src_user and src_user['dep_name'] in admin_deps:
                self.top_control=1
            else:
                self.top_control=0

            if 'post' in src_user:
                self.post = src_user['post']
                session['post']=self.post

            if 'dep_name' in src_user:
                self.dep_name = src_user['dep_name']
                session['dep_name']=self.dep_name

            if src_user['fio'] in ldap_admins:
                log.info(f'----------------\n\tUSER {session['username']} are Admin\n----------------')
                self.roles='Admin'
            else:
                self.roles='Operator'
            session['roles'] = self.roles

            if 'roles' in src_user:
                self.roles = src_user['roles']
                session['roles']=self.roles
                
            full_name = src_user['fio']
            self.full_name = full_name
            session['full_name'] = full_name 

            self.ip_addr = ip
            log.info(f"LM SSO. SUCCESS\n\tUSERNAME: {self.username}, IP_ADDR: {self.ip_addr}\n\tFIO: {self.full_name}\n\tROLES: {self.roles}, POST: {self.post}\n\tDEP_NAME: {self.dep_name} ")
            return self
        log.info(f"LM SSO. F`AIL. USERNAME: {src_user}, ip_addr: {ip}, password: {session['password']}")
        return None

    def have_role(self, role_name):
        if hasattr(self, 'roles'):
            return role_name in self.roles

    def is_authenticated(self):
        if not hasattr(self, 'username'):
            return False
        else:
            return True

    def is_active(self):
        if hasattr(self, 'username'):
            return True
        else:
            return False

    def is_anonymous(self):
        if not hasattr(self, 'username'):
            return True
        else:
            return False

    def get_id(self):
        log.debug(f'LDAP_User. GET_ID. self.src_user: {self.src_user}, self.username: {self.username}')
        if hasattr(self, 'src_user'):
            return self.src_user
        else: 
            return None


if __name__ == "__main__":
    #'bind_dn'       => 'cn=ldp,ou=admins,dc=gfss,dc=kz',
    #'bind_pass'     => 'hu89_fart7',    
    #connect_ldap('Гусейнов', '123')
    log.debug(f'__main__ function')

App:GrocerySplit. Multi-tenant grocery expense splitter. Users→groups(households)→monthly lists→items→settlements.
STACK: BE=Python3.12/FastAPI/SQLAlchemy-async(aiosqlite+asyncpg)/Pydantic/python-jose(JWT-HS256-24h)/passlib[bcrypt]/Uvicorn FE=Vue3(CompositionAPI,script-setup)/VueRouter4/Pinia/TS/TailwindCSS4/Axios/vue-chartjs/date-fns/Vite INFRA=Docker(python:3.12-slim+uvicorn,nginx:alpine+ViteSPA),docker-compose,SQLite-default/Postgres-optional
MODELS:
User:id,username(uniq),password(bcrypt,never-serialize),display_name,is_admin,must_change_password,created_at
Group:id,name,created_at→hasMany(GroupMember,List)
GroupMember:group_id,user_id(non-admin only)
List:group_id,name,month(1-12),year,status(active|archived),split_type(equal|custom),created_at,archived_at;max-1-active-per-group
Item:list_id,user_id,description,cost(float,NOT NULL),category,date_purchased,notes,receipt_path,created_at
Settlement:list_id,user_id,amount_owed,amount_paid(def0),is_settled(defF),settled_at
ShoppingItem:group_id,created_by,description,category,notes,quantity(text),is_purchased(defF),purchased_at,purchased_by,linked_item_id(FK→Item),created_at
AuditLog:actor(uid),actor_name,action(eg user.create/auth.login.success),target_type,target_id,details,ip,created_at
API(/api):
PUBLIC: GET/health POST/login
AUTH: GET/me POST/change-password
GROUPS: GET/my-groups
LISTS: GET/lists/active?group_id GET/lists/archived?group_id GET/lists/:id POST/lists POST/lists/:id/archive
ITEMS: GET/items(filters:list_id,group_id,q,category,user_id,min_cost,max_cost,from,to,status,sort,limit,offset) GET/items/:id POST/items PUT/items/:id DELETE/items/:id
FILES: POST/upload/receipt(multipart,jpg/jpeg/png/pdf) GET/receipts/:id
SETTLEMENTS: GET/lists/:id/settlements/calculate GET/lists/:id/settlements POST/lists/:id/settlements/mark-paid
SHOPPING: GET/shopping?group_id&status POST/shopping PUT/shopping/:id DELETE/shopping/:id POST/shopping/:id/purchase(→creates-Item)
ANALYTICS: GET/analytics?group_id&months→monthly_trend,per_user,by_category,top_items,totals
ADMIN(is_admin): CRUD/admin/users CRUD/admin/groups +/admin/groups/:id/members CRUD/admin/lists +archive GET/admin/stats GET/admin/audit-logs(filters:action,actor,target_type,q,from,to,limit,offset)
SPLIT: equal=total/non-admin-count(admins excluded),FE shows transfer suggestions. custom=each user owes sum of own items. mark-paid→amount_paid+is_settled=true
PAGES(src/views/):
/login:user/pass,emerald-teal-gradient,GrocerySplit🛒
/change-password:forced-first-login,strength-meter(8+chars,letter,number,symbol)
/dashboard:summary-bar(total,count,per-person),tabs(Items|Settlement),add-item+receipt,settlement-breakdown+mark-paid,archive
/items:filter-panel(text,category,flatmate,cost-range,date-range,sort),paginated-25
/shopping:tabs(ToBuy|Purchased),mark-purchased→real-expense
/analytics:KPI-cards,trend-line/bar,per-user-bar,category-doughnut,top10-table,range(3/6/12/24mo)
/archived:accordion-past-months+items+settlements
/admin:stats-bar,tabs(Users|Groups|Lists|Audit),CRUD,audit-log-viewer
COMPONENTS(src/components/):AppHeader(sticky-nav,group-switcher,emerald/slate-theme) BaseButton(variants:primary-emerald/secondary-gray/danger-rose/ghost/warning-amber,sizes:sm/md/lg,loading) BaseCard+EmptyState+LoadingScreen+ErrorBanner FormField(slots) BaseModal(Teleport,esc/click-outside) ToastNotification(Pinia-store,auto-dismiss-4s,rose/emerald) ConfirmButton(two-step-arm-confirm) GroupPicker ItemRow(emoji,color-badge)
AUTH: JWT-localStorage,Axios-interceptors(inject-token,401→logout). VueRouter-beforeEach-guard(must_change_password). FastAPI-Depends(get_current_user,get_admin_user). Bootstrap-admin-on-startup(lifespan,env:ADMIN_USERNAME/PASSWORD/DISPLAY_NAME,must_change_password=true). Last-admin-protection. Pinia:auth.ts(user,token,login,logout),toast.ts. useSelectedGroup-composable(auto-load,localStorage-persist,auto-select-single)
CATEGORIES:Vegetables🥦Fruits🍎Dairy🥛Meat🥩Snacks🍪Beverages🧃Household🧹Other🛒
COLORS:8-palette(violet,blue,amber,rose,teal,pink,indigo,lime)deterministic-per-group,used-avatars/items/charts
ENV:PORT=8080 DB_DRIVER=sqlite DATABASE_PATH=./grocery.db DATABASE_URL=(pg) JWT_SECRET UPLOADS_DIR=./uploads FRONTEND_ORIGIN=http://localhost:3000 ADMIN_USERNAME=admin ADMIN_PASSWORD=admin123
STRUCTURE:
app/{main,config,database,models,schemas,dependencies}.py app/routers/{auth,groups,lists,items,files,settlements,shopping,analytics,admin,audit}.py app/utils/{jwt,calculations,audit}.py requirements.txt
frontend/src/{main.ts,App.vue} frontend/src/router/index.ts frontend/src/stores/{auth,toast}.ts frontend/src/composables/useSelectedGroup.ts frontend/src/views/{Login,ChangePassword,Dashboard,Items,Shopping,Analytics,Archived,Admin}View.vue frontend/src/components/{AppHeader,BaseButton,BaseCard,EmptyState,LoadingScreen,ErrorBanner,FormField,BaseModal,ToastNotification,ConfirmButton,GroupPicker,ItemRow}.vue frontend/src/lib/{api,types,colors}.ts
Docker:python:3.12-slim+uvicorn,Vite+nginx:alpine,docker-compose+healthchecks. Seed:scripts/seed.py(reset+create-admin). start.sh/stop.sh(local-dev,PID-tracking)
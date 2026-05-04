import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

// 懒加载组件
const Dict = () => import('@/views/DictPage.vue')
const Home = () => import('@/views/Home.vue')

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        component: () => import('@/views/DictLayout.vue'),
        children: [
            {
                path: '',
                name: 'Home',
                component: Home
            },
            {
                path: 'dict/:id',
                name: 'Dict',
                component: Dict
            }
        ]
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

// 👇 加上这个：默认打开 /dict/95
router.beforeEach((to, _, next) => {
    if (to.path === '/') {
        next('/dict/95')
    } else {
        next()
    }
})

export default router

import Vue from 'vue'
import Router from 'vue-router'

import throughput from '../components/throughput'
import connections from '../components/connections'
import performance from '../components/performance'
import innodb from '../components/innodb'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/'
    },
    {
      path: '/monitor/throughput',
      component: throughput
    },
    {
      path: '/monitor/connections',
      component: connections
    },
    {
      path: '/monitor/performance',
      component: performance
    },
    {
      path: '/monitor/innodb',
      component: innodb
    }
  ]
})

<script setup lang="ts">
import dayjs from 'dayjs'
import type { DataTableColumns } from 'naive-ui'

type Transaction = {
  id: number
  type: string
  currency: string
  amount: number
  fee_rate: number
  exchange_rate: number
  operator_id: number
  is_correction: boolean
  created_at: string
}

type User = {
  id: number
  username: string
  joined_at: string
}

const token = useQueryStr('token', { showError: true })

const model = reactive({
  date: Date.now()
})

const { data, execute, error } = useAsyncData<{
  inflow_without_correction: Transaction[]
  inflow_with_correction: Transaction[]
  outflow_without_correction: Transaction[]
  outflow_with_correction: Transaction[]
  operators: User[]
}>(() => $fetch(`/api/bill`, { params: { token: token.value, date: dayjs(model.date).format('YYYY-MM-DD') } }), {
  default: () => ({
    inflow_without_correction: [],
    inflow_with_correction: [],
    outflow_without_correction: [],
    outflow_with_correction: [],
    operators: []
  })
})

const columns: DataTableColumns<Transaction> = [
  {
    title: '类型',
    key: 'type',
    render: (row) => (row.type === 'income' ? '入账' : '下发')
  },
  {
    title: '币种',
    key: 'currency',
    render: (row) => (row.currency === 'CNY' ? '人民币' : '?')
  },
  {
    title: '金额',
    key: 'amount',
    render: (row) => `${row.amount} ${row.currency}`
  },
  {
    title: '转换为 USDT',
    key: 'amount_usdt',
    render: (row) => `${((row.amount / row.exchange_rate) * (1 - row.fee_rate)).toFixed(2)} USDT`
  },
  {
    title: '费率',
    key: 'fee_rate',
    render: (row) => `${row.fee_rate * 100}%`
  },
  {
    title: '汇率',
    key: 'exchange_rate'
  },
  {
    title: '操作人',
    key: 'operator',
    render: (row) => data.value.operators.find((x) => x.id === row.operator_id)?.username
  },
  {
    title: '修正',
    key: 'is_correction',
    render: (row) => (row.is_correction ? '是' : '否')
  },
  {
    title: '时间',
    key: 'created_at',
    render: (row) => dayjs(row.created_at).format('HH:mm:ss')
  }
]
</script>

<template>
  <div class="flex flex-col items-center p-8 min-h-100dvh bg-gray-50">
    <div class="flex flex-col gap-8 w-full max-w-270">
      <NCard class="shadow" content-class="flex gap-4">
        <label class="flex gap-2 items-center">
          <span>选择查询日期:</span>
          <NDatePicker v-model:value="model.date" type="date" :is-date-disabled="disableFutureDates" />
        </label>
        <NButton type="primary" @click="() => execute()">查询账单</NButton>
        <NButton type="primary">导出账单</NButton>
      </NCard>
      <NCard v-if="!error" class="shadow" title="账单详情">
        <h3 class="text-xl font-bold">入款</h3>
        <NDivider />
        <NDataTable :columns="columns" :data="data.inflow_without_correction" />
        <h3 class="text-xl font-bold">出款/下发</h3>
        <NDivider />
        <NDataTable :columns="columns" :data="data.outflow_without_correction" />
        <h3 class="text-xl font-bold">入款修正</h3>
        <NDivider />
        <NDataTable :columns="columns" :data="data.inflow_with_correction" />
        <h3 class="text-xl font-bold">出款修正</h3>
        <NDivider />
        <NDataTable :columns="columns" :data="data.outflow_with_correction" />
      </NCard>
      <NResult v-else :title="error?.statusMessage" :description="`${(error?.data as any)?.detail}`" />
    </div>
  </div>
</template>

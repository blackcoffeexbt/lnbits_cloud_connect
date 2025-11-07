window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  delimiters: ['${', '}'],
  data: function () {
    return {
      currencyOptions: ['sat'],
      settingsFormDialog: {
        show: false,
        data: {}
      },

      ownerDataFormDialog: {
        show: false,
        data: {
          name: null,
          
        }
      },
      ownerDataList: [],
      ownerDataTable: {
        search: '',
        loading: false,
        columns: [
          {"name": "name", "align": "left", "label": "Name", "field": "name", "sortable": true},
          {"name": "updated_at", "align": "left", "label": "Updated At", "field": "updated_at", "sortable": true},
          {"name": "id", "align": "left", "label": "ID", "field": "id", "sortable": true},
          
        ],
        pagination: {
          sortBy: 'updated_at',
          rowsPerPage: 10,
          page: 1,
          descending: true,
          rowsNumber: 10
        }
      },

      clientDataFormDialog: {
        show: false,
        ownerData: {label: 'All Owner Data', value: ''},
        data: {}
      },
      clientDataList: [],
      clientDataTable: {
        search: '',
        loading: false,
        columns: [
          {"name": "name", "align": "left", "label": "Name", "field": "name", "sortable": true},
          {"name": "updated_at", "align": "left", "label": "Updated At", "field": "updated_at", "sortable": true},
          {"name": "id", "align": "left", "label": "ID", "field": "id", "sortable": true},
          
        ],
        pagination: {
          sortBy: 'updated_at',
          rowsPerPage: 10,
          page: 1,
          descending: true,
          rowsNumber: 10
        }
      },

      sshTunnelFormDialog: {
        show: false,
        data: {
          name: '',
          remote_server_user: '',
          remote_server_url: '',
          local_port: null,
          remote_port: null,
          auto_reconnect: true,
          startup_enabled: false
        }
      },
      sshTunnelDetailsDialog: {
        show: false,
        data: {}
      },
      sshTunnelList: [],
      sshTunnelTable: {
        search: '',
        loading: false,
        columns: [
          {"name": "name", "align": "left", "label": "Name", "field": "name", "sortable": true},
          {"name": "remote_server_url", "align": "left", "label": "Server", "field": "remote_server_url", "sortable": true},
          {"name": "local_port", "align": "left", "label": "Local Port", "field": "local_port", "sortable": true},
          {"name": "remote_port", "align": "left", "label": "Remote Port", "field": "remote_port", "sortable": true},
          {"name": "is_connected", "align": "left", "label": "Status", "field": "is_connected", "sortable": true},
          {"name": "startup_enabled", "align": "left", "label": "Startup", "field": "startup_enabled", "sortable": true},
          {"name": "created_at", "align": "left", "label": "Created", "field": "created_at", "sortable": true}
        ],
        pagination: {
          sortBy: 'created_at',
          rowsPerPage: 10,
          page: 1,
          descending: true,
          rowsNumber: 10
        }
      }
    }
  },
  watch: {
    'ownerDataTable.search': {
      handler() {
        const props = {}
        if (this.ownerDataTable.search) {
          props['search'] = this.ownerDataTable.search
        }
        this.getOwnerData()
      }
    },
    'clientDataTable.search': {
      handler() {
        const props = {}
        if (this.clientDataTable.search) {
          props['search'] = this.clientDataTable.search
        }
        this.getClientData()
      }
    },
    'clientDataFormDialog.ownerData.value': {
      handler() {
        const props = {}
        if (this.clientDataTable.search) {
          props['search'] = this.clientDataTable.search
        }
        this.getClientData()
      }
    },
    'sshTunnelTable.search': {
      handler() {
        this.getSSHTunnels()
      }
    }
  },

  methods: {
    //////////////// Settings ////////////////////////
    async updateSettings() {
      
      try {
        const data = {...this.settingsFormDialog.data}

        await LNbits.api.request(
          'PUT',
          '/lnbits_cloud_connect/api/v1/settings',
          null,
          data
        )
        this.settingsFormDialog.show = false
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },
    async getSettings() {
      
      try {
        const {data} = await LNbits.api.request(
          'GET',
          '/lnbits_cloud_connect/api/v1/settings',
          null
        )
        this.settingsFormDialog.data = data
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },
    async showSettingsDataForm() {
      await this.getSettings()
      this.settingsFormDialog.show = true
    },

    //////////////// Owner Data ////////////////////////
    async showNewOwnerDataForm() {
      this.ownerDataFormDialog.data = {
          name: null,
          
      }
      this.ownerDataFormDialog.show = true
    },
    async showEditOwnerDataForm(data) {
      this.ownerDataFormDialog.data = {...data}
      this.ownerDataFormDialog.show = true
    },
    async saveOwnerData() {
      
      try {
        const data = {extra: {}, ...this.ownerDataFormDialog.data}
        const method = data.id ? 'PUT' : 'POST'
        const entry = data.id ? `/${data.id}` : ''
        await LNbits.api.request(
          method,
          '/lnbits_cloud_connect/api/v1/owner_data' + entry,
          null,
          data
        )
        this.getOwnerData()
        this.ownerDataFormDialog.show = false
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    async getOwnerData(props) {
      
      try {
        this.ownerDataTable.loading = true
        const params = LNbits.utils.prepareFilterQuery(
          this.ownerDataTable,
          props
        )
        const {data} = await LNbits.api.request(
          'GET',
          `/lnbits_cloud_connect/api/v1/owner_data/paginated?${params}`,
          null
        )
        this.ownerDataList = data.data
        this.ownerDataTable.pagination.rowsNumber = data.total
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      } finally {
        this.ownerDataTable.loading = false
      }
    },
    async deleteOwnerData(ownerDataId) {
      await LNbits.utils
        .confirmDialog('Are you sure you want to delete this Owner Data?')
        .onOk(async () => {
          try {
            
            await LNbits.api.request(
              'DELETE',
              '/lnbits_cloud_connect/api/v1/owner_data/' + ownerDataId,
              null
            )
            await this.getOwnerData()
          } catch (error) {
            LNbits.utils.notifyApiError(error)
          }
        })
    },
    async exportOwnerDataCSV() {
      await LNbits.utils.exportCSV(
        this.ownerDataTable.columns,
        this.ownerDataList,
        'owner_data_' + new Date().toISOString().slice(0, 10) + '.csv'
      )
    },

    //////////////// Client Data ////////////////////////
    async showEditClientDataForm(data) {
      this.clientDataFormDialog.data = {...data}
      this.clientDataFormDialog.show = true
    },
    async saveClientData() {
      
      try {
        const data = {extra: {}, ...this.clientDataFormDialog.data}
        const method = data.id ? 'PUT' : 'POST'
        const entry = data.id ? `/${data.id}` : ''
        await LNbits.api.request(
          method,
          '/lnbits_cloud_connect/api/v1/client_data' + entry,
          null,
          data
        )
        this.getClientData()
        this.clientDataFormDialog.show = false
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    async getClientData(props) {
      
      try {
        this.clientDataTable.loading = true
        let params = LNbits.utils.prepareFilterQuery(
          this.clientDataTable,
          props
        )
        const ownerDataId = this.clientDataFormDialog.ownerData.value
        if (ownerDataId) {
          params += `&owner_data_id=${ownerDataId}`
        }
        const {data} = await LNbits.api.request(
          'GET',
          `/lnbits_cloud_connect/api/v1/client_data/paginated?${params}`,
          null
        )
        this.clientDataList = data.data
        this.clientDataTable.pagination.rowsNumber = data.total
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      } finally {
        this.clientDataTable.loading = false
      }
    },
    async deleteClientData(clientDataId) {
      await LNbits.utils
        .confirmDialog('Are you sure you want to delete this Client Data?')
        .onOk(async () => {
          try {
            
            await LNbits.api.request(
              'DELETE',
              '/lnbits_cloud_connect/api/v1/client_data/' + clientDataId,
              null
            )
            await this.getClientData()
          } catch (error) {
            LNbits.utils.notifyApiError(error)
          }
        })
    },

    async exportClientDataCSV() {
      await LNbits.utils.exportCSV(
        this.clientDataTable.columns,
        this.clientDataList,
        'client_data_' + new Date().toISOString().slice(0, 10) + '.csv'
      )
    },

    //////////////// SSH Tunnels ////////////////////////
    async showNewSSHTunnelForm() {
      this.sshTunnelFormDialog.data = {
        name: '',
        remote_server_user: '',
        remote_server_url: '',
        local_port: null,
        remote_port: null,
        auto_reconnect: true,
        startup_enabled: false
      }
      this.sshTunnelFormDialog.show = true
    },

    async showEditSSHTunnelForm(tunnel) {
      this.sshTunnelFormDialog.data = {...tunnel}
      this.sshTunnelFormDialog.show = true
    },

    async saveSSHTunnel() {
      try {
        const data = {...this.sshTunnelFormDialog.data}
        const method = data.id ? 'PUT' : 'POST'
        const url = data.id 
          ? `/lnbits_cloud_connect/api/v1/ssh-tunnels/${data.id}`
          : '/lnbits_cloud_connect/api/v1/ssh-tunnels'
        
        await LNbits.api.request(method, url, null, data)
        this.getSSHTunnels()
        this.sshTunnelFormDialog.show = false
        this.$q.notify({
          type: 'positive',
          message: data.id ? 'SSH tunnel updated successfully!' : 'SSH tunnel created successfully! Public key generated for server setup.'
        })
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    async getSSHTunnels(props) {
      try {
        this.sshTunnelTable.loading = true
        const params = LNbits.utils.prepareFilterQuery(
          this.sshTunnelTable,
          props
        )
        const {data} = await LNbits.api.request(
          'GET',
          `/lnbits_cloud_connect/api/v1/ssh-tunnels?${params}`,
          null
        )
        this.sshTunnelList = data.data
        this.sshTunnelTable.pagination.rowsNumber = data.total
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      } finally {
        this.sshTunnelTable.loading = false
      }
    },

    async toggleSSHTunnel(tunnel) {
      try {
        const action = tunnel.is_connected ? 'disconnect' : 'connect'
        const {data} = await LNbits.api.request(
          'POST',
          `/lnbits_cloud_connect/api/v1/ssh-tunnels/${tunnel.id}/${action}`,
          null
        )
        
        this.$q.notify({
          type: 'positive',
          message: data.message
        })
        
        await this.getSSHTunnels()
        
        // Auto-refresh tunnel status
        if (action === 'connect') {
          setTimeout(() => this.getSSHTunnels(), 2000)
        }
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },

    async showSSHTunnelDetails(tunnel) {
      this.sshTunnelDetailsDialog.data = {...tunnel}
      this.sshTunnelDetailsDialog.show = true
    },

    async deleteSSHTunnel(tunnelId) {
      await LNbits.utils
        .confirmDialog('Are you sure you want to delete this SSH tunnel?')
        .onOk(async () => {
          try {
            await LNbits.api.request(
              'DELETE',
              `/lnbits_cloud_connect/api/v1/ssh-tunnels/${tunnelId}`,
              null
            )
            await this.getSSHTunnels()
            this.$q.notify({
              type: 'positive',
              message: 'SSH tunnel deleted successfully'
            })
          } catch (error) {
            LNbits.utils.notifyApiError(error)
          }
        })
    },

    //////////////// Utils ////////////////////////
    dateFromNow(date) {
      return moment(date).fromNow()
    },
    async fetchCurrencies() {
      try {
        const response = await LNbits.api.request('GET', '/api/v1/currencies')
        this.currencyOptions = ['sat', ...response.data]
      } catch (error) {
        LNbits.utils.notifyApiError(error)
      }
    },
    
    copyToClipboard(text, message = 'Copied to clipboard!') {
      navigator.clipboard.writeText(text).then(() => {
        this.$q.notify({
          type: 'positive',
          message: message
        })
      }).catch(err => {
        console.error('Failed to copy: ', err)
        this.$q.notify({
          type: 'negative',
          message: 'Failed to copy to clipboard'
        })
      })
    }
  },
  ///////////////////////////////////////////////////
  //////LIFECYCLE FUNCTIONS RUNNING ON PAGE LOAD/////
  ///////////////////////////////////////////////////
  async created() {
    this.fetchCurrencies()
    this.getOwnerData()
    this.getClientData()
    this.getSSHTunnels()
    
    // Set up periodic refresh for SSH tunnel status
    setInterval(() => {
      this.getSSHTunnels()
    }, 30000) // Refresh every 30 seconds
  }
})
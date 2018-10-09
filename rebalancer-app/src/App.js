import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
// import Auth from '@aws-amplify/auth';
import Analytics from '@aws-amplify/analytics';

// import awsconfig from './aws-exports';
import Amplify, { API } from 'aws-amplify';
import aws_exports from './aws-exports';

import ReactTable from "react-table";
import 'react-table/react-table.css'

// retrieve temporary AWS credentials and sign requests
// Auth.configure(awsconfig);
// send analytics events to Amazon Pinpoint
// Analytics.configure(awsconfig);

// API.configure(awsconfig);

Amplify.configure(aws_exports);

const positions_columns = [{
  Header: 'symbol',
  accessor: 'symbol'
}, {
  Header: 'composition',
  accessor: 'composition'
}, {
  Header: 'allocation',
  accessor: 'allocation'
}, {
  Header: 'averageEntryPrice',
  accessor: 'averageEntryPrice'
}, {
  Header: 'currentPrice',
  accessor: 'currentPrice'
}, {
  Header: 'openQuantity',
  accessor: 'openQuantity'
}, {
  Header: 'currentMarketValue',
  accessor: 'currentMarketValue'
}, {
  Header: 'purchaseQuantity',
  accessor: 'purchaseQuantity'
}, {
  Header: 'purchaseValue',
  accessor: 'purchaseValue'
}, {
  Header: 'newQuantity',
  accessor: 'newQuantity'
}, {
  Header: 'newMarketValue',
  accessor: 'newMarketValue'
}, {
  Header: 'before actual %',
  accessor: 'before actual %'
}, {
  Header: 'after actual %',
  accessor: 'after actual %'
}, {
  Header: 'ideal %',
  accessor: 'ideal %'
}];

const balances_columns = [{
  Header: 'name',
  accessor: 'name'
}, {
  Header: 'value',
  accessor: 'value'
}];


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      analyticsEventSent: false, 
      resultHtml: "", 
      eventsSent: 0,
      portfolio: {}
    };
  }

  componentDidMount() {
    let apiName = 'rebalancerapi';
    let path = '/portfolios/object/51680711/latest';
    API.get(apiName, path).then(response => {
      console.log(response);
      this.setState({
        portfolio: response
      });
    }).catch(error => {
        console.log(error.response)
    });
  }

  render() {
    return (
      <div className="App">
        <h1>Positions</h1>
        <ReactTable
          data={this.state.portfolio.positions}
          columns={positions_columns}
          resolveData={data => Object.keys(data).map(k => Object.assign(data[k], {symbol: k}))}
          pageSize={7}
        />
        <h1>Balances</h1>
        <ReactTable
          data={this.state.portfolio.balances}
          columns={balances_columns}
          resolveData={data => Object.keys(data).map(k => ({name: k, value: data[k]}))}
          pageSize={7}
        />
      </div>
    );
  }
}

export default App;

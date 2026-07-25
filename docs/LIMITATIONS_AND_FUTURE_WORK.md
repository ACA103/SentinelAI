# Limitations & Future Work

## Current Limitations
1. **Synthetic Data**: The models are currently trained and validated on synthetic data.
2. **Batch Processing**: The pipeline currently executes in batch mode (`.parquet` files) rather than real-time streaming.

## Future Work
1. **Real-time Streaming**: Migrate the Pandas/Parquet data layer to Apache Kafka and Apache Flink for real-time stream processing.
2. **Distributed Inference**: Deploy models behind FastAPI microservices using Kubernetes.
3. **Active Directory Integration**: Connect the data generator directly to live LDAP/Azure AD feeds.

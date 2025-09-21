KUBECONFIG_OUTPUT=

SA_NAME=
SECRET_NAME=
NAMESPACE=

for i in {1..10}; do
	TOKEN=$(kubectl get secret "${SECRET_NAME}" -n "${NAMESPACE}" -o jsonpath='{.data.token}' 2>/dev/null || true)
	if [[ -n "$TOKEN" ]]; then
		break
	fi
	sleep 1
done

if [[ -z "$TOKEN" ]]; then
	echo ":x: ERROR: Token not available in secret"
	exit 1
fi

TOKEN=$(echo "$TOKEN" | base64 --decode)
CA_CERT=$(kubectl get secret "${SECRET_NAME}" -n "${NAMESPACE}" -o jsonpath='{.data.ca\.crt}' | base64 --decode)

cat <<EOF >"${KUBECONFIG_OUTPUT}"
apiVersion: v1
kind: Config
clusters:
- name: ${SA_NAME}
  cluster:
    certificate-authority-data: $(echo "${CA_CERT}" | base64 | tr -d '\n')
    server: $(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
contexts:
- name: ${SA_NAME}
  context:
    cluster: ${SA_NAME}
    namespace: ${NAMESPACE}
    user: ${SA_NAME}
users:
- name: ${SA_NAME}
  user:
    token: ${TOKEN}
EOF

echo ":white_check_mark: Done. Kubeconfig written to: ${KUBECONFIG_OUTPUT}"

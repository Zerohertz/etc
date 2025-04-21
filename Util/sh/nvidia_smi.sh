#!/bin/sh

# 디버깅 활성화 여부
DEBUG=0

# 칼럼 너비 정의 (각 값은 해당 칼럼에 할당된 너비)
COL_WIDTH_GPU_IDX=8    # GPU 인덱스 칼럼 너비
COL_WIDTH_MEM=12       # GPU 메모리 사용량 칼럼 너비
COL_WIDTH_PID=10       # 프로세스 ID 칼럼 너비
COL_WIDTH_NAMESPACE=14 # 네임스페이스 칼럼 너비
COL_WIDTH_POD_NAME=40  # 파드 이름 칼럼 너비
COL_WIDTH_REQ_GPU=12   # GPU 요청 자원 칼럼 너비
COL_WIDTH_LIMIT_GPU=12 # GPU 제한 자원 칼럼 너비
COL_WIDTH_CMD=0        # 명령어는 가변 너비 (나머지 공간 사용)

debug_log() {
	if [ "$DEBUG" -eq 1 ]; then
		echo "DEBUG: $1" >&2
	fi
}

create_separator() {
	local separator=""
	local total_width=0
	total_width=$(tput cols)
	separator=$(printf '%*s' "$total_width" | tr ' ' '-')
	echo "$separator"
}

# 필요한 명령어 확인
command -v nvidia-smi >/dev/null 2>&1 || {
	echo "Error: nvidia-smi command not found"
	exit 1
}
command -v kubectl >/dev/null 2>&1 || {
	echo "Error: kubectl command not found"
	exit 1
}

# jq 명령어 확인
JQ_AVAILABLE=0
if command -v jq >/dev/null 2>&1; then
	JQ_AVAILABLE=1
	debug_log "jq found, using optimized data processing"
else
	debug_log "jq not found, performance will be suboptimal"
fi

# 컨테이너 ID로 파드 정보 조회 - 개별 명령어 사용
get_pod_info_by_container_id() {
	local container_id="$1"
	local short_id=$(echo "$container_id" | cut -c 1-12)
	debug_log "Looking up pod by container ID: $short_id"

	# 컨테이너 ID 형식이 완전한지 확인
	if [ -z "$container_id" ]; then
		return 1
	fi

	# 컨테이너 ID를 단순화하여 조회 - jq 없이도 작동
	if command -v crictl >/dev/null 2>&1; then
		local container_json
		container_json=$(crictl inspect "$container_id" 2>/dev/null)
		local exit_code=$?

		if [ $exit_code -eq 0 ] && [ -n "$container_json" ]; then
			debug_log "Container found with crictl"
			local pod_id=$(echo "$container_json" | grep -o '"pod_sandbox_id": "[^"]*' | sed 's/"pod_sandbox_id": "//' 2>/dev/null)

			if [ -n "$pod_id" ]; then
				local pod_json
				pod_json=$(crictl inspectp "$pod_id" 2>/dev/null)

				if [ $? -eq 0 ] && [ -n "$pod_json" ]; then
					local pod_namespace=$(echo "$pod_json" | grep -o '"namespace": "[^"]*' | sed 's/"namespace": "//' | head -1)
					local pod_name=$(echo "$pod_json" | grep -o '"name": "[^"]*' | sed 's/"name": "//' | head -1)

					if [ -n "$pod_namespace" ] && [ -n "$pod_name" ]; then
						echo "$pod_namespace,$pod_name"
						return 0
					fi
				fi
			fi
		fi
	fi

	# crictl이 실패하거나 없으면 kubectl로 시도
	local kubectl_output
	kubectl_output=$(kubectl get pods --all-namespaces -o=custom-columns=NS:.metadata.namespace,NAME:.metadata.name,CONTAINERS:.status.containerStatuses[*].containerID 2>/dev/null | grep -i "$short_id")

	if [ -n "$kubectl_output" ]; then
		local pod_namespace=$(echo "$kubectl_output" | awk '{print $1}')
		local pod_name=$(echo "$kubectl_output" | awk '{print $2}')

		if [ -n "$pod_namespace" ] && [ -n "$pod_name" ]; then
			debug_log "Found pod via container ID using kubectl: $pod_namespace/$pod_name"
			echo "$pod_namespace,$pod_name"
			return 0
		fi
	fi

	return 1
}

# 캐시된 파드 정보 조회
get_pod_info_by_uid() {
	local pod_uid="$1"
	local pod_data

	if [ -n "$pod_uid" ]; then
		pod_data=$(kubectl get pod --all-namespaces -o=custom-columns=NS:.metadata.namespace,NAME:.metadata.name,UID:.metadata.uid | grep "$pod_uid" 2>/dev/null)

		if [ -n "$pod_data" ]; then
			local pod_namespace=$(echo "$pod_data" | awk '{print $1}')
			local pod_name=$(echo "$pod_data" | awk '{print $2}')

			if [ -n "$pod_namespace" ] && [ -n "$pod_name" ]; then
				debug_log "Found pod via UID: $pod_namespace/$pod_name"
				echo "$pod_namespace,$pod_name"
				return 0
			fi
		fi
	fi

	return 1
}

# GPU 리소스 정보 가져오기
get_gpu_resources() {
	local namespace="$1"
	local pod_name="$2"

	if [ -n "$namespace" ] && [ -n "$pod_name" ]; then
		local resources
		resources=$(kubectl get pod -n "$namespace" "$pod_name" -o jsonpath="{.spec.containers[*].resources.requests.nvidia\.com/gpu},{.spec.containers[*].resources.limits.nvidia\.com/gpu}" 2>/dev/null)

		if [ -n "$resources" ]; then
			echo "$resources"
			return 0
		fi
	fi

	echo "N/A,N/A"
	return 1
}

# jq가 있는 경우 초기 데이터 로드 시도 - 실패시 자동으로 대체 방법 사용
if [ "$JQ_AVAILABLE" -eq 1 ]; then
	debug_log "Trying to prefetch pod information with jq"
	# 안전한 jq 처리를 위한 전처리 시도 (선택적)
	prefetch_success=0
else
	debug_log "jq not available, using direct kubectl lookups"
	prefetch_success=0
fi

# 포맷 문자열 생성
FORMAT_STRING="%-${COL_WIDTH_GPU_IDX}s %-${COL_WIDTH_MEM}s %-${COL_WIDTH_PID}s %-${COL_WIDTH_NAMESPACE}s %-${COL_WIDTH_POD_NAME}s %-${COL_WIDTH_REQ_GPU}s %-${COL_WIDTH_LIMIT_GPU}s %s\n"
SEPARATOR=$(create_separator)

# 줄바꿈이 제대로 되도록 각 줄을 개별적으로 출력
echo "$SEPARATOR"
printf "$FORMAT_STRING" "GPU Idx" "GPU Mem(MB)" "PID" "Namespace" "Pod Name" "Request(GPU)" "Limit(GPU)" "Command"
echo "$SEPARATOR"

# nvidia-smi pmon 실행 및 파싱
nvidia-smi pmon -c 1 -s m | tail -n +3 | while IFS= read -r line; do
	# 빈 줄 건너뛰기
	if [ -z "$line" ]; then
		continue
	fi

	# 공백을 기준으로 필드 분리
	gpu_idx=$(echo "$line" | awk '{print $1}')
	pid=$(echo "$line" | awk '{print $2}')
	type=$(echo "$line" | awk '{print $3}')
	fb=$(echo "$line" | awk '{print $4}')
	ccpm=$(echo "$line" | awk '{print $5}')
	# 6번째 칼럼부터 끝까지는 명령어로 처리
	cmd=$(echo "$line" | awk '{$1=$2=$3=$4=$5=""; print substr($0,6)}')

	# PID가 유효하지 않으면 건너뛰기
	if [ "$pid" = "-" ] || [ -z "$pid" ]; then
		continue
	fi
	# 추가적으로 숫자인지 검사
	case "$pid" in
	'' | *[!0-9]*) continue ;;
	*) ;;
	esac

	debug_log "Processing PID: $pid"

	# /proc/<PID>/cgroup 파일 읽기 시도
	if [ ! -f "/proc/$pid/cgroup" ]; then
		debug_log "cgroup file not found for PID $pid"
		printf "$FORMAT_STRING" "$gpu_idx" "$fb" "$pid" "N/A" "N/A (No cgroup)" "N/A" "N/A" "$cmd"
		continue
	fi

	cgroup_path=$(cat "/proc/$pid/cgroup" 2>/dev/null)
	if [ $? -ne 0 ]; then
		# 프로세스가 사라졌거나 권한 문제
		debug_log "Failed to read cgroup for PID $pid"
		printf "$FORMAT_STRING" "$gpu_idx" "$fb" "$pid" "N/A" "N/A (Proc Err)" "N/A" "N/A" "$cmd"
		continue
	fi

	# 디버그: cgroup 내용 출력
	debug_log "cgroup content for PID $pid: $cgroup_path"

	# 파드 UID 추출 (개선된 버전 - 모든 패턴을 통합)
	pod_uid_with_dashes=""
	container_id=""
	namespace="N/A"
	pod_name="N/A"
	gpu_request="N/A"
	gpu_limit="N/A"

	# 1. 쿠버네티스 패턴 확인 및 UID 추출
	if echo "$cgroup_path" | grep -q 'kubepods'; then
		debug_log "Kubernetes cgroup pattern found for PID $pid"

		# 다양한 UID 패턴 추출 시도 (통합 버전)
		potential_uid=$(echo "$cgroup_path" | grep -o -E 'pod[a-f0-9_-]+' | sed 's/^pod//' | head -n 1)

		if [ -n "$potential_uid" ]; then
			# 언더스코어를 하이픈으로 변환 (필요한 경우)
			pod_uid_with_dashes=$(echo "$potential_uid" | tr '_' '-')
			debug_log "Found pod UID (converted if needed): $pod_uid_with_dashes"
		fi
	fi

	# 2. 컨테이너 ID 추출
	container_id=$(echo "$cgroup_path" | grep -oE '([0-9a-f]{64})' | head -n 1)
	if [ -n "$container_id" ]; then
		debug_log "Found container ID: $container_id"
	fi

	# 3. 순차적으로 정보 검색 시도 - 실패할 경우 다음 방법 시도

	# 3.1 UID로 검색 시도
	if [ -n "$pod_uid_with_dashes" ]; then
		debug_log "Trying to get pod info by UID: $pod_uid_with_dashes"
		pod_info=$(get_pod_info_by_uid "$pod_uid_with_dashes")

		if [ $? -eq 0 ] && [ -n "$pod_info" ]; then
			namespace=$(echo "$pod_info" | cut -d',' -f1)
			pod_name=$(echo "$pod_info" | cut -d',' -f2)
			debug_log "Found pod by UID: $namespace/$pod_name"

			# GPU 리소스 정보 가져오기
			resources=$(get_gpu_resources "$namespace" "$pod_name")
			gpu_request=$(echo "$resources" | cut -d',' -f1)
			gpu_limit=$(echo "$resources" | cut -d',' -f2)
		fi
	fi

	# 3.2 컨테이너 ID로 검색 시도 (UID로 찾지 못한 경우)
	if [ -z "$namespace" ] || [ "$namespace" = "N/A" ] || [ -z "$pod_name" ] || [ "$pod_name" = "N/A" ]; then
		if [ -n "$container_id" ]; then
			debug_log "Trying to get pod info by container ID: $container_id"
			pod_info=$(get_pod_info_by_container_id "$container_id")

			if [ $? -eq 0 ] && [ -n "$pod_info" ]; then
				namespace=$(echo "$pod_info" | cut -d',' -f1)
				pod_name=$(echo "$pod_info" | cut -d',' -f2)
				debug_log "Found pod by container ID: $namespace/$pod_name"

				# GPU 리소스 정보 가져오기
				resources=$(get_gpu_resources "$namespace" "$pod_name")
				gpu_request=$(echo "$resources" | cut -d',' -f1)
				gpu_limit=$(echo "$resources" | cut -d',' -f2)
			fi
		fi
	fi

	# 3.3 Docker 컨테이너 확인 (쿠버네티스에서 찾지 못한 경우)
	if [ -z "$namespace" ] || [ "$namespace" = "N/A" ] || [ -z "$pod_name" ] || [ "$pod_name" = "N/A" ]; then
		if [ -n "$container_id" ] && command -v docker >/dev/null 2>&1; then
			debug_log "Checking docker container ID: $container_id"
			short_id=$(echo "$container_id" | cut -c 1-12)
			container_name=$(docker ps --format '{{.ID}} {{.Names}}' 2>/dev/null | grep -E "^$short_id" | awk '{print $2}')

			if [ -n "$container_name" ]; then
				namespace="docker"
				pod_name="$container_name"
				debug_log "Found docker container: $container_name"
			else
				pod_name="N/A (Non-K8s)"
			fi
		else
			pod_name="N/A (Non-K8s)"
		fi
	fi

	# 값이 없는 경우 처리
	if [ -z "$gpu_request" ] || [ "$gpu_request" = "null" ]; then gpu_request="N/A"; fi
	if [ -z "$gpu_limit" ] || [ "$gpu_limit" = "null" ]; then gpu_limit="N/A"; fi
	if [ -z "$namespace" ] || [ "$namespace" = "null" ]; then namespace="N/A"; fi
	if [ -z "$pod_name" ] || [ "$pod_name" = "null" ]; then pod_name="N/A (Not Found)"; fi

	# 결과 출력
	printf "$FORMAT_STRING" "$gpu_idx" "$fb" "$pid" "$namespace" "$pod_name" "$gpu_request" "$gpu_limit" "$cmd"
done

# 줄바꿈이 제대로 되도록 별도 줄로 출력
echo "$SEPARATOR"

/*==============================================================*/
/* 1. ПОЛЬЗОВАТЕЛЬСКИЕ ПРЕДСТАВЛЕНИЯ (VIEWS)                     */
/*==============================================================*/

CREATE OR REPLACE VIEW v_subscription_activity AS
SELECT 
    s.subscribe_type_id,
    AVG(EXTRACT(EPOCH FROM (v.viewing_finish - v.viewing_start)) / 60) AS avg_time,
    COUNT(DISTINCT v.content_id) AS unique_content
FROM Subscribe s
JOIN Viewing v ON s.user_id = v.user_id
GROUP BY s.subscribe_type_id;

CREATE OR REPLACE VIEW v_daily_revenue AS
SELECT 
    p.payment_date,
    p.subscribe_type_id,
    SUM(p.payment_sum) AS daily_revenue
FROM Payment p
GROUP BY p.payment_date, p.subscribe_type_id;


/*==============================================================*/
/* 2. ХРАНИМЫЕ ПРОЦЕДУРЫ И ТРИГГЕРНЫЕ ФУНКЦИИ                  */
/*==============================================================*/

-- Процедура смены тарифного плана
CREATE OR REPLACE PROCEDURE public.change_subscription_type(
    IN p_user_id integer, 
    IN p_new_subscribe_type_id integer, 
    IN p_payment_method character varying DEFAULT 'карта'::character varying
)
LANGUAGE plpgsql
AS $procedure$
DECLARE
    v_payment_number INT;
    v_subscribe_duration INT;
    v_payment_sum FLOAT8;
BEGIN
    SELECT subscribe_type_duration, subscribe_type_cost 
    INTO v_subscribe_duration, v_payment_sum
    FROM subscribe_type 
    WHERE subscribe_type_id = p_new_subscribe_type_id;

    UPDATE subscribe 
    SET subscribe_finish = CURRENT_DATE - INTERVAL '1 day'
    WHERE user_id = p_user_id AND subscribe_finish >= CURRENT_DATE;

    INSERT INTO subscribe (subscribe_type_id, user_id, subscribe_start, subscribe_finish)
    VALUES (
        p_new_subscribe_type_id, 
        p_user_id, 
        CURRENT_DATE, 
        CURRENT_DATE + (v_subscribe_duration * INTERVAL '1 day')
    )
    ON CONFLICT (subscribe_type_id, user_id, subscribe_start) 
    DO UPDATE SET subscribe_finish = EXCLUDED.subscribe_finish;

    SELECT COALESCE(MAX(payment_number), 0) + 1 INTO v_payment_number 
    FROM payment WHERE user_id = p_user_id;

    INSERT INTO payment (
        user_id, payment_number, subscribe_type_id,
        payment_sum, payment_date, payment_method
    )
    VALUES (
        p_user_id, v_payment_number, p_new_subscribe_type_id,
        v_payment_sum, CURRENT_DATE, p_payment_method
    );
END;
$procedure$;

-- Функция триггера авто-добавления интересов
CREATE OR REPLACE FUNCTION public.auto_add_interests_simple()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    IF NEW.viewing_progress >= 60 THEN
        INSERT INTO interest (user_id, tag_id)
        SELECT NEW.user_id, a.tag_id
        FROM associate a
        WHERE a.content_id = NEW.content_id
          AND NOT EXISTS (
              SELECT 1 
              FROM interest i 
              WHERE i.user_id = NEW.user_id 
                AND i.tag_id = a.tag_id
          );
        
        RAISE NOTICE 'Добавлены интересы для пользователя %', NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$function$;

-- Функция триггера обновления временной метки завершения просмотра
CREATE OR REPLACE FUNCTION public.update_viewing_finish_timestamp()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
   NEW.viewing_finish = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$function$;


/*==============================================================*/
/* 3. ТРИГГЕРЫ                                                  */
/*==============================================================*/

CREATE OR REPLACE TRIGGER trg_auto_add_interests 
AFTER INSERT ON public.viewing 
FOR EACH ROW 
EXECUTE FUNCTION auto_add_interests_simple();

CREATE OR REPLACE TRIGGER trg_update_viewing_finish 
BEFORE UPDATE ON public.viewing 
FOR EACH ROW 
EXECUTE FUNCTION update_viewing_finish_timestamp();